from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import SalesOrder, SalesOrderItem
from app.schemas.schemas import SalesOrderCreate

class CRUDSalesOrder(CRUDBase[SalesOrder, SalesOrderCreate, Any]):
    def get_by_company(self, db: Session, *, company_id: int, skip: int = 0, limit: int = 100) -> List[SalesOrder]:
        return db.query(SalesOrder).filter(SalesOrder.company_id == company_id).offset(skip).limit(limit).all()

    def create_with_items(self, db: Session, *, obj_in: SalesOrderCreate) -> SalesOrder:
        # Create the order first
        order_data = obj_in.dict(exclude={'items'})
        db_order = SalesOrder(**order_data)
        db.add(db_order)
        db.flush()  # Flush to get the ID
        
        # Create order items
        for item_data in obj_in.items:
            db_item = SalesOrderItem(
                sales_order_id=db_order.id,
                **item_data.dict()
            )
            db.add(db_item)
        
        db.commit()
        db.refresh(db_order)
        return db_order

sales_order = CRUDSalesOrder(SalesOrder)