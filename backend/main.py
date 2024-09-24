from fastapi import FastAPI, Depends, File, UploadFile, Form, HTTPException, status
from sqlalchemy.orm import sessionmaker, Session, joinedload
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from datetime import timedelta, datetime
from jose import JWTError, jwt
from backend.models import CartAction, Product, User,ProductResponse, UserCreate, LoginRequest, ProductCreate, Cart
import shutil
import os



# Settings
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30

# Database connection
DATABASE_URL = "postgresql://postgres:159753@localhost:5432/marketplace_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory for uploaded images
UPLOAD_FOLDER = "static/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.mount("/static", StaticFiles(directory="static"), name="static")

# OAuth2 password scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Token creation and validation
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=1)
    expire = expire + timedelta(days=1)
    to_encode.update({"exp": expire})
    # Ensure 'sub' is a string
    to_encode["sub"] = str(to_encode["sub"])  # Convert user ID to string

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Endpoints
@app.get("/products", response_model=list[ProductResponse])
def get_all_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = (
        db.query(Product, User.full_address)
        .join(User, Product.user_id == User.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Combine the product details with the user's full address
    product_data = [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "quantity": product.quantity,
            "image": product.image,
            "full_address": full_address  # Add full address to the product data
        }
        for product, full_address in products
    ]

    return product_data


@app.get("/total_pages", response_model=dict)
def get_total_pages(limit: int = 10, db: Session = Depends(get_db)):
    total_count = db.query(Product).count()
    total_pages = (total_count + limit - 1) // limit
    return {"total_pages": total_pages}

@app.post("/products")
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    print(f"Received token: {token}")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        expire_time = payload.get("exp")
        print(f"Token expiration time: {expire_time}")  # Log the expiration time for debugging

        if datetime.utcfromtimestamp(expire_time) < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")

        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Save the uploaded image to the static/uploads folder
    upload_path = os.path.join(UPLOAD_FOLDER, image.filename)
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Proceed to add the product
    new_product = Product(
        name=name,
        description=description,
        price=price,
        quantity=quantity,
        image=image.filename,  # Save only the filename
        user_id=user.id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    print(f"Product created: {new_product.name}")
    return {"message": "Product created successfully", "product_id": new_product.id}


@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)

    return {"token": access_token, "token_type": "bearer", "user_id": user.id, "first_name": user.first_name}


@app.get("/user_products/{user_id}", response_model=list[ProductResponse])
def get_user_products(user_id: int, db: Session = Depends(get_db)):
    products = db.query(Product).options(joinedload(Product.user)).filter(Product.user_id == user_id).all()

    # Map full_address from user to each product response
    product_responses = []
    for product in products:
        product_response = ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            quantity=product.quantity,
            image=product.image,
            full_address=product.user.full_address  # Fetch full_address from the related User
        )
        product_responses.append(product_response)

    return product_responses



@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        expire_time = payload.get("exp")
        
        if datetime.utcfromtimestamp(expire_time) < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")

        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        # Fetch the product
        product = db.query(Product).filter(Product.id == product_id, Product.user_id == user.id).first()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found or unauthorized")
        
        # Delete the product
        db.delete(product)
        db.commit()
        return {"message": "Product deleted successfully"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    


# Route to add an item to the cart
@app.post("/cart")
def add_to_cart(action: CartAction, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    # Check if product exists
    product = db.query(Product).filter(Product.id == action.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if the item is already in the cart
    cart_item = db.query(Cart).filter(Cart.user_id == user_id, Cart.product_id == action.product_id).first()
    if cart_item:
        cart_item.quantity += action.quantity
    else:
        cart_item = Cart(user_id=user_id, product_id=action.product_id, quantity=action.quantity)
        db.add(cart_item)

    db.commit()
    return {"message": "Item added to cart"}

# Route to view the cart
@app.get("/cart")
def view_cart(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
    return cart_items

# Route to remove an item from the cart
@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    cart_item = db.query(Cart).filter(Cart.user_id == user_id, Cart.product_id == product_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}