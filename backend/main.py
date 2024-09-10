from fastapi import FastAPI, Depends
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine
from fastapi import HTTPException
from passlib.context import CryptContext
from backend.models import Product
from fastapi import HTTPException
from backend.models import User



# Database connection
DATABASE_URL = "postgresql://postgres:159753@localhost:5432/marketplace_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity
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

# Pydantic model for API response
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int
    image_url: str  # Add this line for the image URL

    class Config:
        orm_mode = True  # Enable ORM mode for SQLAlchemy models

# Define the expected structure for the registration data
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    full_address: str

class LoginRequest(BaseModel):
    email: str
    password: str

# Endpoint to get all products with pagination
@app.get("/products", response_model=list[ProductResponse])
def get_all_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

# Endpoint to calculate and return total pages
@app.get("/total_pages", response_model=dict)
def get_total_pages(limit: int = 10, db: Session = Depends(get_db)):
    total_count = db.query(Product).count()  # Get total number of products
    total_pages = (total_count + limit - 1) // limit  # Calculate number of pages
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



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    if not verify_password(request.password, user.password):  
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    return {"message": "Login successful", "user_id": user.id}

# Registration endpoint
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_password,
        full_address=user.full_address
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Registration successful", "user_id": new_user.id}
