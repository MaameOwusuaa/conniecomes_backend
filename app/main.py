from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles
from app.routers import auth, users, categories, products, cart
from app.routers.order import router as order_router
from app.routers.payment import router as payment_router
from app.routers.booking import router as booking_router
from app.routers.admin import router as admin_router
from app.routers.services import router as services_router
from app.routers.contact import router as contact_router
from app.core.config import settings
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
app.include_router(admin_router)
app.include_router(services_router)
app.include_router(contact_router)

uploads_path = settings.UPLOAD_DIR
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")

@app.get("/")
def root():
    return {
        "message": "API is running"
    }
