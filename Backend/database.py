from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Create the Database File (SQLite)
# In production (SDS), this would be the PostgreSQL URL.
SQLALCHEMY_DATABASE_URL = "sqlite:///./waf.db"

# 2. Configure the Connection
# check_same_thread=False is needed for SQLite + FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Create the Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base Class for Models
Base = declarative_base()

# 5. Dependency for FastAPI (Opens/Closes connection per request)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()