from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.CompanyRead])
def read_companies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve companies.
    """
    companies = crud.company.get_multi(db, skip=skip, limit=limit)
    return companies

@router.post("/", response_model=schemas.CompanyRead)
def create_company(
    *,
    db: Session = Depends(get_db),
    company_in: schemas.CompanyCreate,
) -> Any:
    """
    Create new company.
    """
    company = crud.company.create(db, obj_in=company_in)
    return company

@router.get("/{company_id}", response_model=schemas.CompanyRead)
def read_company(
    company_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    Get company by ID.
    """
    company = crud.company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.delete("/{company_id}")
def delete_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
) -> Any:
    """
    Delete company.
    """
    company = crud.company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    company = crud.company.remove(db, id=company_id)
    return {"message": "Company deleted successfully"}