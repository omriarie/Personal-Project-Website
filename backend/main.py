from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


# Database connection
DATABASE_URL = "postgresql://postgres:159753@localhost:5432/marketplace_db"

# Create the engine and sessionmaker
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the base class for models
Base = declarative_base()

app = FastAPI()



# Define the Product model (SQLAlchemy model)
class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    date_added = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic model for API response
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int

    class Config:
        orm_mode = True


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to be more specific if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to get all products from the database
@app.get("/products", response_model=list[ProductResponse])
def get_all_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products


@app.get("/total_pages", response_model=dict)
def get_total_pages(limit: int = 10, db: Session = Depends(get_db)):
    total_count = db.query(Product).count()  # Get the total number of products
    total_pages = (total_count + limit - 1) // limit  # Calculate the number of pages
    return {"total_pages": total_pages}



# Endpoint to get a product by its ID from the database
@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        return {"error": "Product not found"}
    return product



# Endpoint to create a new product in the database
@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductResponse, db: Session = Depends(get_db)):
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        quantity=product.quantity
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

