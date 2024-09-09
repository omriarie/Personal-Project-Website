#! C:\Users\ADMIN\Documents\GitHub\Personal-Project-Website\backend\venv\Scripts\python.exe
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column ,Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

# Define the same database URL used in table_maker.py
DATABASE_URL = "postgresql://postgres:159753@localhost:5432/marketplace_db"

# Create the engine and sessionmaker
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for models (if needed for future extensions)
Base = declarative_base()

# Define the Product model (same as in table_maker.py)
class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    date_added = Column(DateTime(timezone=True), server_default=func.now())

# Create a Pydantic model for the response
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int

    class Config:
        orm_mode = True

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Create the tables in the PostgreSQL database
def create_tables():
    Base.metadata.create_all(bind=engine)

def insert_test_products():
    # Create a session
    db = SessionLocal()
    
    try:
        # Data to be inserted
        test_products = [
            Product(name="Inserted Product 1", description="Description 1", price=9.99, quantity=10),
            Product(name="Inserted Product 2", description="Description 2", price=19.99, quantity=5),
            Product(name="Inserted Product 3", description="Description 3", price=29.99, quantity=2),
        ]

        # Insert the data into the database
        db.add_all(test_products)
        db.commit()

        print("Products added successfully!")
    except Exception as e:
        db.rollback()
        print(f"Failed to insert products: {e}")
    finally:
        db.close()

# Run the insert function when the script is executed directly
if __name__ == "__main__":
    insert_test_products()