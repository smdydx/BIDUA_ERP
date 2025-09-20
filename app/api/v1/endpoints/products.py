from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.ProductRead])
def read_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve products.
    """
    products = crud.product.get_multi(db, skip=skip, limit=limit)
    return products

@router.post("/", response_model=schemas.ProductRead)
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: schemas.ProductCreate,
) -> Any:
    """
    Create new product.
    """
    product = crud.product.get_by_sku(db, sku=product_in.sku)
    if product:
        raise HTTPException(
            status_code=400,
            detail="Product with this SKU already exists.",
        )
    product = crud.product.create(db, obj_in=product_in)
    return product

@router.get("/{product_id}", response_model=schemas.ProductRead)
def read_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    Get product by ID.
    """
    product = crud.product.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=schemas.ProductRead)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: schemas.ProductUpdate,
) -> Any:
    """
    Update product.
    """
    product = crud.product.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product = crud.product.update(db, db_obj=product, obj_in=product_in)
    return product

@router.delete("/{product_id}")
def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
) -> Any:
    """
    Delete product.
    """
    product = crud.product.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product = crud.product.remove(db, id=product_id)
    return {"message": "Product deleted successfully"}

@router.get("/category/{category_id}", response_model=List[schemas.ProductRead])
def read_products_by_category(
    category_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get products by category.
    """
    products = crud.product.get_by_category(db, category_id=category_id, skip=skip, limit=limit)
    return products