from fastapi import FastAPI
from fastapi import APIRouter
from app.routers import auth, users, categories, products, cart
from app.routers.order import router as order_router
from app.routers.payment import router as payment_router
from app.routers.booking import router as booking_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Conniecomes Beauty Salon API", 
    version="1.0.0", 
    description="API for Conniecomes Beauty Salon")


router = APIRouter()

"""
@router.get("/")
def home():
    return {"message": "Welcome to Conniecomes Beauty Salon API!"}
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)    
app.include_router(router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(booking_router)

@app.get("/")
def root():
    return {
        "message": "API is running"
    }

