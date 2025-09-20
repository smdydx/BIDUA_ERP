from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import Account, JournalEntry, JournalEntryLine
from app.schemas.schemas import JournalEntryCreate

class CRUDAccount(CRUDBase[Account, Any, Any]):
    def get_by_code(self, db: Session, *, code: str) -> Optional[Account]:
        return db.query(Account).filter(Account.code == code).first()

    def get_by_type(self, db: Session, *, account_type: str, skip: int = 0, limit: int = 100) -> List[Account]:
        return db.query(Account).filter(Account.account_type == account_type).offset(skip).limit(limit).all()

account = CRUDAccount(Account)

class CRUDJournalEntry(CRUDBase[JournalEntry, JournalEntryCreate, Any]):
    def create_with_lines(self, db: Session, *, obj_in: JournalEntryCreate) -> JournalEntry:
        # Create the journal entry first
        entry_data = obj_in.dict(exclude={'lines'})
        db_entry = JournalEntry(**entry_data)
        db.add(db_entry)
        db.flush()  # Flush to get the ID
        
        # Create journal entry lines
        for line_data in obj_in.lines:
            db_line = JournalEntryLine(
                journal_entry_id=db_entry.id,
                **line_data.dict()
            )
            db.add(db_line)
        
        db.commit()
        db.refresh(db_entry)
        return db_entry

journal_entry = CRUDJournalEntry(JournalEntry)