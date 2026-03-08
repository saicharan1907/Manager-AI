import sqlite3
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_superuser = Column(Integer, default=0)
    
    files = relationship("UploadedFile", back_populates="owner")
    products = relationship("Product", back_populates="owner")
    sales = relationship("Sale", back_populates="owner")

class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    file_path = Column(String)
    file_type = Column(String) # 'inventory' or 'sales'
    
    owner = relationship("User", back_populates="files")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    sku = Column(String, index=True, unique=True)
    category = Column(String, default="Uncategorized")
    current_stock = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    price = Column(Float, default=0.0)
    
    owner = relationship("User", back_populates="products")
    sales = relationship("Sale", back_populates="product")

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)
    sale_date = Column(DateTime, default=datetime.datetime.utcnow)
    
    owner = relationship("User", back_populates="sales")
    product = relationship("Product", back_populates="sales")
