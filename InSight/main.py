from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

# Import get_db from its new location
from . import models, schemas, crud, auth
from .database import engine, get_db

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
def create_data_point(
    item: schemas.DataPointCreate, 
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_user) # Now protected
):
    return crud.create_data_point(db=db, item=item)

@app.get("/data/latest", response_model=schemas.DataPoint)
def read_latest_data(
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_user) # Now protected
):
    latest_point = crud.get_latest_data_point(db)
    if latest_point is None:
        raise HTTPException(status_code=404, detail="No data available")
    return latest_point

@app.get("/data/history", response_model=list[schemas.DataPoint])
def read_data_history(
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_user) # Now protected
):
    return crud.get_data_points_history(db=db)


print("INFO:     API documentation available at http://127.0.0.1:8000/docs")