from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import Company, Address
from app.schemas.schemas import CompanyCreate, CompanyRead

class CRUDCompany(CRUDBase[Company, CompanyCreate, Any]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Company]:
        return db.query(Company).filter(Company.name == name).first()

    def get_by_gstin(self, db: Session, *, gstin: str) -> Optional[Company]:
        return db.query(Company).filter(Company.gstin == gstin).first()

company = CRUDCompany(Company)

class CRUDAddress(CRUDBase[Address, Any, Any]):
    pass

address = CRUDAddress(Address)