from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.EmployeeRead])
def read_employees(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve employees.
    """
    employees = crud.employee.get_multi(db, skip=skip, limit=limit)
    return employees

@router.post("/", response_model=schemas.EmployeeRead)
def create_employee(
    *,
    db: Session = Depends(get_db),
    employee_in: schemas.EmployeeBase,
) -> Any:
    """
    Create new employee.
    """
    employee = crud.employee.create(db, obj_in=employee_in)
    return employee

@router.get("/{employee_id}", response_model=schemas.EmployeeRead)
def read_employee(
    employee_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    Get employee by ID.
    """
    employee = crud.employee.get(db, id=employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.delete("/{employee_id}")
def delete_employee(
    *,
    db: Session = Depends(get_db),
    employee_id: int,
) -> Any:
    """
    Delete employee.
    """
    employee = crud.employee.get(db, id=employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    employee = crud.employee.remove(db, id=employee_id)
    return {"message": "Employee deleted successfully"}