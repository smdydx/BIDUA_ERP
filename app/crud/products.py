from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import Product, Category
from app.schemas.schemas import ProductCreate, ProductUpdate

class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def get_by_sku(self, db: Session, *, sku: str) -> Optional[Product]:
        return db.query(Product).filter(Product.sku == sku).first()

    def get_by_category(self, db: Session, *, category_id: int, skip: int = 0, limit: int = 100) -> List[Product]:
        return db.query(Product).filter(Product.category_id == category_id).offset(skip).limit(limit).all()

    def get_active_products(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Product]:
        return db.query(Product).filter(Product.is_active == True).offset(skip).limit(limit).all()

product = CRUDProduct(Product)

class CRUDCategory(CRUDBase[Category, Any, Any]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Category]:
        return db.query(Category).filter(Category.name == name).first()

category = CRUDCategory(Category)