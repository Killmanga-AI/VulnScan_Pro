# app/routes/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta
from typing import Dict

from app.core.database import get_db
from app.core.models import User
from app.core.auth import create_access_token
from app.core.auth_utils import hash_password, verify_password

router = APIRouter()

# ----------------------------
# Pydantic Schemas
# ----------------------------

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

# ----------------------------
# Routes
# ----------------------------

@router.post("/register")
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password safely
    hashed_password = hash_password(payload.password)

    # Create user
    new_user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hashed_password,
        scan_credits=5,
        plan_tier="free"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user_id": new_user.id,
        "scan_credits": new_user.scan_credits
    }


@router.post("/login")
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == payload.email).first()

    if not db_user or not verify_password(payload.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create JWT access token
    token_data: Dict[str, str] = {"sub": str(db_user.id), "email": db_user.email}
    access_token = create_access_token(token_data, expires_delta=timedelta(minutes=60 * 24))

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "email": db_user.email,
        "scan_credits": db_user.scan_credits
    }

@router.post("/token")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm provides form_data.username and form_data.password
    db_user = db.query(User).filter(User.email == form_data.username).first()

    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token_data = {"sub": str(db_user.id), "email": db_user.email}
    access_token = create_access_token(token_data, expires_delta=timedelta(minutes=60 * 24))

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "email": db_user.email,
        "scan_credits": db_user.scan_credits
    }