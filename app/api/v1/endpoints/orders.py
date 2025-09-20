from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.SalesOrderRead])
def read_sales_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve sales orders.
    """
    orders = crud.sales_order.get_multi(db, skip=skip, limit=limit)
    return orders

@router.post("/", response_model=schemas.SalesOrderRead)
def create_sales_order(
    *,
    db: Session = Depends(get_db),
    order_in: schemas.SalesOrderCreate,
) -> Any:
    """
    Create new sales order.
    """
    order = crud.sales_order.create_with_items(db, obj_in=order_in)
    return order

@router.get("/{order_id}", response_model=schemas.SalesOrderRead)
def read_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    Get sales order by ID.
    """
    order = crud.sales_order.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Sales order not found")
    return order

@router.delete("/{order_id}")
def delete_sales_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
) -> Any:
    """
    Delete sales order.
    """
    order = crud.sales_order.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Sales order not found")
    order = crud.sales_order.remove(db, id=order_id)
    return {"message": "Sales order deleted successfully"}