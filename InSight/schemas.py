from pydantic import BaseModel
from datetime import datetime

# This schema is for data coming INTO our API (e.g., from the simulator)
class DataPointCreate(BaseModel):
    name: str
    value: float

# This schema is for data going OUT of our API (e.g., to the frontend)
class DataPoint(DataPointCreate):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True # This tells Pydantic to read the data from a SQLAlchemy model

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True