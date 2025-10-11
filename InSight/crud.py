from sqlalchemy.orm import Session

from InSight import auth

from . import models, schemas

def create_data_point(db: Session, item: schemas.DataPoint):
    # 1. Create a SQLAlchemy model instance from the API data.
    db_item = models.DataPoint(name=item.name, value=item.value)

    # 2. Add the new item to the database session.
    db.add(db_item)

    # 3. Commit the changes to the database (save them).
    db.commit()

    # 4. Refresh the item to get the new data from the database (like the auto-generated id and timestamp).
    db.refresh(db_item)

    return db_item

from . import models

def get_latest_data_point(db: Session):
    # Query the DataPoint table, order by timestamp descending, and get the first result.
    return db.query(models.DataPoint).order_by(models.DataPoint.timestamp.desc()).first()

def get_data_points_history(db: Session, limit: int = 30):
    result = db.query(models.DataPoint).order_by(models.DataPoint.timestamp.desc()).limit(limit).all()
    return result[::-1] # Reverse the list

def get_user_by_username(db: Session, username: str):
    """Finds a user by their username."""
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Creates a new user with a hashed password."""
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user