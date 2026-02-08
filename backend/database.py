# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# --- MySQL Configuration ---
DB_USER = "root"          # <-- your MySQL username
DB_PASSWORD = "password"  # <-- your MySQL password
DB_HOST = "localhost"     # usually localhost
DB_PORT = "3306"          # default MySQL port
DB_NAME = "expense_tracker"  # make sure this DB exists in MySQL

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# --- SQLAlchemy Setup ---
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

