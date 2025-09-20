from fastapi import APIRouter

from app.api.v1.endpoints import users, products, companies, orders, employees, accounts

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])