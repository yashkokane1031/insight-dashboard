from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from jose import JWTError, jwt

# Import get_db from its new location
from . import models, schemas, crud, auth
from .database import engine, get_db
from .websocket_manager import manager

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="InSight API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The get_db function is now removed from here

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the InSight API!"}

# --- Authentication Endpoints ---
@app.post("/users/", response_model=schemas.User)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

# --- Data Endpoints ---
@app.post("/data/", response_model=schemas.DataPoint)
async def create_data_point(
    item: schemas.DataPointCreate, 
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """Create a new data point and broadcast to all connected WebSocket clients."""
    data_point = crud.create_data_point(db=db, item=item)
    
    # Broadcast to all connected WebSocket clients
    await manager.broadcast_data_point({
        "id": data_point.id,
        "name": data_point.name,
        "value": data_point.value,
        "timestamp": data_point.timestamp.isoformat()
    })
    
    return data_point

@app.get("/data/latest", response_model=schemas.DataPoint)
def read_latest_data(
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    latest_point = crud.get_latest_data_point(db)
    if latest_point is None:
        raise HTTPException(status_code=404, detail="No data available")
    return latest_point

@app.get("/data/history", response_model=list[schemas.DataPoint])
def read_data_history(
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    return crud.get_data_points_history(db=db)

@app.get("/data/forecast")
def get_forecast(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """
    Generate ML-based forecast for the next hour.
    
    Returns:
        - predicted: List of predicted values with timestamps and confidence intervals
        - anomalies: Data points that deviate significantly from expected values
        - model_info: Information about the model used
    """
    from .ml_forecaster import create_forecast
    
    # Get historical data
    history = crud.get_data_points_history(db=db, limit=500)  # More data for better predictions
    
    if len(history) < 10:
        raise HTTPException(
            status_code=400, 
            detail="Insufficient data for forecasting. Need at least 10 data points."
        )
    
    # Convert to format expected by forecaster
    data_points = [
        {
            "timestamp": dp.timestamp.isoformat(),
            "value": dp.value
        }
        for dp in history
    ]
    
    # Generate forecast
    forecast = create_forecast(data_points)
    
    return forecast


# --- WebSocket Endpoint ---
@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time data streaming.
    
    Connect with: ws://localhost:8000/ws?token=<your_jwt_token>
    
    Messages are JSON objects with format:
    {
        "type": "new_data",
        "payload": { "id": int, "name": str, "value": float, "timestamp": str }
    }
    """
    # Validate JWT token
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            await websocket.close(code=4001, reason="Invalid token")
            return
    except JWTError:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    # Accept connection and add to manager
    await manager.connect(websocket)
    
    try:
        # Keep connection alive and listen for client messages
        while True:
            # We don't expect messages from the client, but we need to keep listening
            # to detect disconnects
            data = await websocket.receive_text()
            # Optionally handle ping/pong or other client messages here
    except WebSocketDisconnect:
        manager.disconnect(websocket)


print("INFO:     API documentation available at http://127.0.0.1:8000/docs")
print("INFO:     WebSocket endpoint available at ws://127.0.0.1:8000/ws?token=<jwt>")