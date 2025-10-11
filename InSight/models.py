from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

# We import the Base class from our database.py file.
# Our model will inherit from this class.
from .database import Base

class DataPoint(Base):
    # This attribute tells SQLAlchemy the name of the table to use in the database.
    __tablename__ = "data_points"

    # These are the columns of our table.
    # id will be our unique primary key for each data point.
    id = Column(Integer, primary_key=True, index=True)
    
    # The name of the metric (e.g., "cpu_load"). Indexing makes searching by name faster.
    name = Column(String, index=True)
    
    # The actual value of the metric.
    value = Column(Float)
    
    # A timestamp for when the data was recorded.
    # `server_default=func.now()` tells the database to automatically set the
    # current time when a new data point is created.
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)