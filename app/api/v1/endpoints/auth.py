
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import crud, schemas
from app.core.database import get_db
from app.core.auth import (
    verify_password, 
    create_access_token, 
    get_current_user,
    get_current_active_user,
    get_password_hash
)
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

@router.post("/login", response_model=schemas.Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Login endpoint - returns JWT token
    """
    # Check if user exists
    user = crud.user.get_by_email(db, email=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/register", response_model=schemas.UserRead)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Register new user
    """
    # Check if user already exists
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Create user with hashed password
    user_data = user_in.model_dump()
    user_data["hashed_password"] = get_password_hash(user_in.password)
    del user_data["password"]
    
    user = crud.user.create(db, obj_in=user_data)
    return user

@router.get("/me", response_model=schemas.UserRead)
def read_current_user(
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Get current user profile
    """
    return current_user

@router.put("/me", response_model=schemas.UserRead)
def update_current_user(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    user_in: schemas.UserUpdate,
) -> Any:
    """
    Update current user profile
    """
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user
