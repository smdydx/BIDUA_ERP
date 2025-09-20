from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.AccountRead])
def read_accounts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve accounts.
    """
    accounts = crud.account.get_multi(db, skip=skip, limit=limit)
    return accounts

@router.post("/", response_model=schemas.AccountRead)
def create_account(
    *,
    db: Session = Depends(get_db),
    account_in: schemas.AccountBase,
) -> Any:
    """
    Create new account.
    """
    account = crud.account.create(db, obj_in=account_in)
    return account

@router.get("/{account_id}", response_model=schemas.AccountRead)
def read_account(
    account_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    Get account by ID.
    """
    account = crud.account.get(db, id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.post("/journal-entries/", response_model=schemas.JournalEntryRead)
def create_journal_entry(
    *,
    db: Session = Depends(get_db),
    entry_in: schemas.JournalEntryCreate,
) -> Any:
    """
    Create new journal entry.
    """
    entry = crud.journal_entry.create_with_lines(db, obj_in=entry_in)
    return entry

@router.get("/journal-entries/", response_model=List[schemas.JournalEntryRead])
def read_journal_entries(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve journal entries.
    """
    entries = crud.journal_entry.get_multi(db, skip=skip, limit=limit)
    return entries