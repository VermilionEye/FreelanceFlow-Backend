from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core import security
from app.core.config import settings
from app.db.base import get_db
from app.models.user import User
from app.schemas.user import UserCreate, Token, LoginRequest
from datetime import timedelta, datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    logger.info("=== Login Process Started ===")
    logger.info(f"Login attempt for email: {login_data.email}")
    
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not security.verify_password(login_data.password, user.hashed_password):
        logger.error(f"Login failed for email: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info("Password verification successful")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": login_data.email}, expires_delta=access_token_expires
    )
    logger.info(f"Generated new access token: {access_token[:10]}...")
    
    # Обновляем токен в базе данных
    logger.info("Updating token in database...")
    user.access_token = access_token
    user.token_expires = datetime.utcnow() + access_token_expires
    user.last_login = datetime.utcnow()
    
    try:
        db.commit()
        logger.info("Token successfully saved to database")
    except Exception as e:
        logger.error(f"Error saving token to database: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving authentication data"
        )
    
    logger.info("=== Login Process Completed ===")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = security.get_password_hash(user_data.password)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user_data.email}, expires_delta=access_token_expires
    )
    
    db_user = User(
        username=user_data.email,
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        access_token=access_token,
        token_expires=datetime.utcnow() + access_token_expires,
        registration_date=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"access_token": access_token, "token_type": "bearer"} 