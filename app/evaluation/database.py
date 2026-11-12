
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Use DATABASE_PATH if provided; otherwise use the existing local database
DATABASE_PATH = Path(
    os.environ.get(
        "DATABASE_PATH",
        str(BASE_DIR / "evaluation_history.db")
    )
)

# Ensure the database directory exists
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# SQLite database location
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for database models
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
