from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. This is the connection string for our database.
# It tells SQLAlchemy where our database is located.
# Format: "postgresql://<user>:<password>@<host>:<port>/<dbname>"
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost:5433/insightdb"

# 2. The "engine" is the main entry point for SQLAlchemy to talk to the database.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. A "session" is like a conversation with the database. We create a
# SessionLocal class here which we will use to create new sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. We will use this Base class to create our database table models (as Python classes).
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()