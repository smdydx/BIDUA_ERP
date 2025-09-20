from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Numeric, Text, Table, Index
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base(cls=AsyncAttrs)

# association tables
role_permission = Table(
    "role_permission", Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)

user_role = Table(
    "user_role", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), index=True)  # Index for search
    is_active = Column(Boolean, default=True, index=True)  # Index for filtering
    created_at = Column(DateTime, default=datetime.utcnow, index=True)  # Index for sorting

    roles = relationship("Role", secondary=user_role, back_populates="users")
    
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),  # Composite index
        Index('idx_user_created_active', 'created_at', 'is_active'),
    )

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255))

    permissions = relationship("Permission", secondary=role_permission, back_populates="roles")
    users = relationship("User", secondary=user_role, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True)
    code = Column(String(128), unique=True, nullable=False, index=True)
    description = Column(String(255))

    roles = relationship("Role", secondary=role_permission, back_populates="permissions")

class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True)
    line1 = Column(String(255), nullable=False)
    line2 = Column(String(255))
    city = Column(String(100), index=True)  # Index for city searches
    state = Column(String(100), index=True)  # Index for state searches
    postal_code = Column(String(32), index=True)  # Index for postal code searches
    country = Column(String(100), default="India", index=True)
    
    __table_args__ = (
        Index('idx_address_city_state', 'city', 'state'),
        Index('idx_address_postal_country', 'postal_code', 'country'),
    )

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)  # Index for company search
    gstin = Column(String(32), unique=True, index=True)  # Index for GSTIN lookup
    contact_email = Column(String(255), index=True)
    contact_phone = Column(String(50), index=True)
    address_id = Column(Integer, ForeignKey("addresses.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    address = relationship("Address")
    
    __table_args__ = (
        Index('idx_company_name_active', 'name', 'created_at'),
    )

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    parent = relationship("Category", remote_side=[id])

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    sku = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)  # Index for product search
    description = Column(Text)
    unit_price = Column(Numeric(12,2), nullable=False, index=True)  # Index for price range queries
    cost_price = Column(Numeric(12,2), index=True)
    is_active = Column(Boolean, default=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), index=True)
    
    category = relationship("Category")
    
    __table_args__ = (
        Index('idx_product_name_active', 'name', 'is_active'),
        Index('idx_product_category_active', 'category_id', 'is_active'),
        Index('idx_product_price_range', 'unit_price', 'is_active'),
    )

class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    location = Column(String(255))

class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    change = Column(Integer, nullable=False, index=True)
    reason = Column(String(255))
    occurred_at = Column(DateTime, default=datetime.utcnow, index=True)

    product = relationship("Product")
    warehouse = relationship("Warehouse")
    
    __table_args__ = (
        Index('idx_stock_product_date', 'product_id', 'occurred_at'),
        Index('idx_stock_warehouse_date', 'warehouse_id', 'occurred_at'),
        Index('idx_stock_product_warehouse', 'product_id', 'warehouse_id'),
    )

class SalesOrder(Base):
    __tablename__ = "sales_orders"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    order_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, index=True)
    notes = Column(Text)

    company = relationship("Company")
    items = relationship("SalesOrderItem", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_order_company_date', 'company_id', 'order_date'),
        Index('idx_order_due_date', 'due_date'),
        Index('idx_order_date_range', 'order_date', 'due_date'),
    )

class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"
    id = Column(Integer, primary_key=True)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, index=True)
    unit_price = Column(Numeric(12,2), nullable=False)

    product = relationship("Product")
    
    __table_args__ = (
        Index('idx_orderitem_order_product', 'sales_order_id', 'product_id'),
    )

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    code = Column(String(64))
    account_type = Column(String(50))
    balance = Column(Numeric(14,2), default=0)

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    narration = Column(Text)
    
    lines = relationship("JournalEntryLine", cascade="all, delete-orphan")

class JournalEntryLine(Base):
    __tablename__ = "journal_entry_lines"
    id = Column(Integer, primary_key=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    debit = Column(Numeric(14,2), default=0)
    credit = Column(Numeric(14,2), default=0)
    narration = Column(Text)

    account = relationship("Account")

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(150), nullable=False, index=True)
    last_name = Column(String(150), index=True)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(50), index=True)
    emp_code = Column(String(64), unique=True, index=True)
    joined_at = Column(Date, index=True)
    
    __table_args__ = (
        Index('idx_employee_name', 'first_name', 'last_name'),
        Index('idx_employee_joined', 'joined_at'),
    )

class Attendance(Base):
    __tablename__ = "attendances"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    check_in = Column(DateTime, index=True)
    check_out = Column(DateTime, index=True)

    employee = relationship("Employee")
    
    __table_args__ = (
        Index('idx_attendance_emp_date', 'employee_id', 'date'),
        Index('idx_attendance_date_range', 'date', 'check_in', 'check_out'),
    )