from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.api import deps
from app.core.database import get_db
from app.core.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[schemas.UserRead])
def read_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve users (requires authentication).
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users

# User creation is now handled by /auth/register endpoint

@router.get("/{user_id}", response_model=schemas.UserRead)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    Get user by ID (requires authentication).
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
) -> Any:
    """
    Update user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}")
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
) -> Any:
    """
    Delete user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = crud.user.remove(db, id=user_id)
    return {"message": "User deleted successfully"}