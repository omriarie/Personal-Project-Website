from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel

Base = declarative_base()

# Define the Product model (SQLAlchemy model)
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    image = Column(String, nullable=True)  # Add this line
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="products")


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    full_address = Column(String, nullable=False)
    products = relationship("Product", back_populates="user")
    cart_items = relationship("Cart", back_populates="user")


class Cart(Base):
    __tablename__ = "cart"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer, default=1)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product")



# Response model for products
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int
    image: str
    full_address: str

    class Config:
        from_attributes = True

# Schema for creating a product
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    quantity: int

# Schema for user creation
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    full_address: str

# Schema for login requests
class LoginRequest(BaseModel):
    email: str
    password: str

# Pydantic model for cart actions
class CartAction(BaseModel):
    product_id: int
    quantity: int