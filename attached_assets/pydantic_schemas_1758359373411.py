from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, condecimal, constr
from pydantic import constr, condecimal

# ---- Base ----
class IDModel(BaseModel):
    id: int

    class Config:
        orm_mode = True

# ---- User / Auth ----
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str]
    is_active: bool = True


UserCreate_Password = constr(min_length=8)

class UserCreate(UserBase):
    password:str= UserCreate_Password

class UserUpdate(BaseModel):
    full_name: Optional[str]
    is_active: Optional[bool]

class UserRead(UserBase, IDModel):
    created_at: datetime

# ---- Role & Permission ----
class PermissionBase(BaseModel):
    code: str
    description: Optional[str]

class PermissionRead(PermissionBase, IDModel):
    pass

class RoleBase(BaseModel):
    name: str
    description: Optional[str]

class RoleRead(RoleBase, IDModel):
    permissions: List[PermissionRead] = []

# ---- Contacts & Address ----
class AddressBase(BaseModel):
    line1: str
    line2: Optional[str]
    city: str
    state: Optional[str]
    postal_code: Optional[str]
    country: str = "India"

class AddressRead(AddressBase, IDModel):
    pass

class ContactBase(BaseModel):
    phone: Optional[str]
    email: Optional[EmailStr]
    address: Optional[AddressBase]

# ---- Customer / Supplier ----
class CompanyBase(BaseModel):
    name: str
    gstin: Optional[str]
    contact: Optional[ContactBase]

class CompanyCreate(CompanyBase):
    pass

class CompanyRead(CompanyBase, IDModel):
    created_at: datetime

# ---- Product / Inventory ----
class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int]

class CategoryRead(CategoryBase, IDModel):
    pass

ProductBase_SKU =constr(max_length=64)

ProductBase_UNIT_PRICE = condecimal(max_digits=12, decimal_places=2) 

ProductBase_COST_PRICE= Optional[condecimal(max_digits=12, decimal_places=2)]

class ProductBase(BaseModel):
    sku:str= ProductBase_SKU
    name: str
    description: Optional[str]
    unit_price:float= ProductBase_UNIT_PRICE
    cost_price: ProductBase_COST_PRICE
    is_active: bool = True
    category_id: Optional[int]

class ProductCreate(ProductBase):
    initial_stock: Optional[int] = 0


ProductUpdate_Unit_price = Optional[condecimal(max_digits=12, decimal_places=2)]

class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    unit_price:float= ProductUpdate_Unit_price
    is_active: Optional[bool]

class ProductRead(ProductBase, IDModel):
    category: Optional[CategoryRead]
    available_stock: int = 0

# ---- Warehouse & Stock ----
class WarehouseBase(BaseModel):
    name: str
    location: Optional[str]

class WarehouseRead(WarehouseBase, IDModel):
    pass

class StockMovementBase(BaseModel):
    product_id: int
    warehouse_id: int
    change: int
    reason: Optional[str]
    occurred_at: Optional[datetime]

class StockMovementRead(StockMovementBase, IDModel):
    occurred_at: datetime

# ---- Sales / Purchase ----


OrderItemBase_Unit_price = condecimal(max_digits=12, decimal_places=2)

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price:float= OrderItemBase_Unit_price

class OrderBase(BaseModel):
    company_id: int
    order_date: date
    due_date: Optional[date]
    notes: Optional[str]

class SalesOrderCreate(OrderBase):
    items: List[OrderItemBase]


SalesOrderRead_Total_Amount = condecimal(max_digits=14, decimal_places=2)

class SalesOrderRead(OrderBase, IDModel):
    total_amount: float =SalesOrderRead_Total_Amount
    items: List[OrderItemBase]


# ---- Accounting ----
class AccountBase(BaseModel):
    name: str
    code: Optional[str]
    account_type: str  # e.g. Asset, Liability, Equity, Revenue, Expense


AccountRead_Balance = condecimal(max_digits=14, decimal_places=2) = 0

class AccountRead(AccountBase, IDModel):
    balance: float =AccountRead_Balance




JournalEntryLine_Debit = Optional[condecimal(max_digits=14, decimal_places=2)] = 0

JournalEntryLine_Credit =  Optional[condecimal(max_digits=14, decimal_places=2)] = 0

class JournalEntryLine(BaseModel):
    account_id: int
    debit: float = JournalEntryLine_Debit
    credit: float = JournalEntryLine_Credit
    narration: Optional[str]

class JournalEntryCreate(BaseModel):
    date: date
    narration: Optional[str]
    lines: List[JournalEntryLine]

class JournalEntryRead(IDModel):
    date: date
    narration: Optional[str]
    lines: List[JournalEntryLine]

# ---- HR / Employee ----
class EmployeeBase(BaseModel):
    first_name: str
    last_name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    emp_code: Optional[str]

class EmployeeRead(EmployeeBase, IDModel):
    joined_at: Optional[date]

class AttendanceRecord(BaseModel):
    employee_id: int
    date: date
    check_in: Optional[datetime]
    check_out: Optional[datetime]

# ---- Pagination / Filters ----
class Pagination(BaseModel):
    page: int = 1
    size: int = 25

class FilterResponse(BaseModel):
    total: int
    page: int
    size: int