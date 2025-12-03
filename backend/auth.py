from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import models, schemas, utils
from backend.database import get_db
from jose import jwt

from datetime import datetime, timedelta

router = APIRouter()

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"


@router.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    db_user = db.query(models.User).filter(models.User.user_name == user.user_name).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pw = utils.hash_password(user.password)
    new_user = models.User(
        user_name=user.user_name,
        password=hashed_pw,
        user_email=user.user_email,
        contact_num_1=user.contact_num_1,
        contact_num_2=user.contact_num_2,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}


@router.post("/login")
def login_user(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_name == credentials.username).first()

    # 🔹 Username not found
    if not user:
        return {"status": "error", "message": "User does not exist"}

    # 🔹 Wrong password
    if not utils.verify_password(credentials.password, user.password):
        return {"status": "error", "message": "Invalid password"}

    # 🔹 Success
    payload = {
        "sub": user.user_name,
        "exp": datetime.utcnow() + timedelta(hours=2),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "status": "success",
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "username": user.user_name,
        "user_id": user.user_ID
    }
