from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

# Define the Product model (SQLAlchemy model)
class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    date_added = Column(DateTime(timezone=True), server_default=func.now())
    image_url = Column(String, nullable=True)  # Add this line to store image URL


#Define the User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # Storing hashed password
    full_address = Column(Text, nullable=False)
    cart = Column(Text, nullable=True)  # Placeholder for cart logic (you can adjust this later)
    is_admin = Column(Boolean, default=False)  # Optional: Add admin privileges if needed
    
