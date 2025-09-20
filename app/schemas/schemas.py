from typing import Optional, List, Annotated
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field
from decimal import Decimal

# ---- Base ----
class IDModel(BaseModel):
    id: int

    class Config:
        orm_mode = True

# ---- User / Auth ----
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: Annotated[str, Field(min_length=8)]

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserRead(UserBase, IDModel):
    created_at: datetime

# ---- Role & Permission ----
class PermissionBase(BaseModel):
    code: str
    description: Optional[str] = None

class PermissionRead(PermissionBase, IDModel):
    pass

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleRead(RoleBase, IDModel):
    permissions: List[PermissionRead] = []

# ---- Contacts & Address ----
class AddressBase(BaseModel):
    line1: str
    line2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "India"

class AddressRead(AddressBase, IDModel):
    pass

class ContactBase(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[AddressBase] = None

# ---- Customer / Supplier ----
class CompanyBase(BaseModel):
    name: str
    gstin: Optional[str] = None
    contact: Optional[ContactBase] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyRead(CompanyBase, IDModel):
    created_at: datetime

# ---- Product / Inventory ----
class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

class CategoryRead(CategoryBase, IDModel):
    pass

class ProductBase(BaseModel):
    sku: Annotated[str, Field(max_length=64)]
    name: str
    description: Optional[str] = None
    unit_price: Annotated[Decimal, Field(max_digits=12, decimal_places=2)]
    cost_price: Optional[Annotated[Decimal, Field(max_digits=12, decimal_places=2)]] = None
    is_active: bool = True
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    initial_stock: Optional[int] = 0

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unit_price: Optional[Annotated[Decimal, Field(max_digits=12, decimal_places=2)]] = None
    is_active: Optional[bool] = None

class ProductRead(ProductBase, IDModel):
    category: Optional[CategoryRead] = None
    available_stock: int = 0

# ---- Warehouse & Stock ----
class WarehouseBase(BaseModel):
    name: str
    location: Optional[str] = None

class WarehouseRead(WarehouseBase, IDModel):
    pass

class StockMovementBase(BaseModel):
    product_id: int
    warehouse_id: int
    change: int
    reason: Optional[str] = None
    occurred_at: Optional[datetime] = None

class StockMovementRead(IDModel):
    product_id: int
    warehouse_id: int
    change: int
    reason: Optional[str] = None
    occurred_at: datetime

# ---- Sales / Purchase ----
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: Annotated[Decimal, Field(max_digits=12, decimal_places=2)]

class OrderBase(BaseModel):
    company_id: int
    order_date: date
    due_date: Optional[date] = None
    notes: Optional[str] = None

class SalesOrderCreate(OrderBase):
    items: List[OrderItemBase]

class SalesOrderRead(OrderBase, IDModel):
    total_amount: Annotated[Decimal, Field(max_digits=14, decimal_places=2)]
    items: List[OrderItemBase]

# ---- Accounting ----
class AccountBase(BaseModel):
    name: str
    code: Optional[str] = None
    account_type: str  # e.g. Asset, Liability, Equity, Revenue, Expense

class AccountRead(AccountBase, IDModel):
    balance: Annotated[Decimal, Field(max_digits=14, decimal_places=2)] = Decimal('0')

class JournalEntryLine(BaseModel):
    account_id: int
    debit: Optional[Annotated[Decimal, Field(max_digits=14, decimal_places=2)]] = Decimal('0')
    credit: Optional[Annotated[Decimal, Field(max_digits=14, decimal_places=2)]] = Decimal('0')
    narration: Optional[str] = None

class JournalEntryCreate(BaseModel):
    date: date
    narration: Optional[str] = None
    lines: List[JournalEntryLine]

class JournalEntryRead(IDModel):
    date: date
    narration: Optional[str] = None
    lines: List[JournalEntryLine]

# ---- HR / Employee ----
class EmployeeBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    emp_code: Optional[str] = None

class EmployeeRead(EmployeeBase, IDModel):
    joined_at: Optional[date] = None

class AttendanceRecord(BaseModel):
    employee_id: int
    date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None

# ---- Pagination / Filters ----
class Pagination(BaseModel):
    page: int = 1
    size: int = 25

class FilterResponse(BaseModel):
    total: int
    page: int
    size: int