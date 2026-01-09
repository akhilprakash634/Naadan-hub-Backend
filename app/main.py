from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.firebase import init_firebase

from app.routers import (
    auth, products, orders, blogs, profile, sellers, admin,
    cart, payments, site_content, reviews, education
)

app = FastAPI(title="FastAPI + Firebase Ecommerce", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.ALLOWED_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _startup():
    init_firebase()

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(blogs.router, prefix="/api/blogs", tags=["Blogs"])
app.include_router(profile.router, prefix="/api/profile", tags=["User Profile"])
app.include_router(sellers.router, prefix="/api/sellers", tags=["Seller Profile"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(payments.router, prefix="/api/payment-methods", tags=["Payment Methods"])
app.include_router(site_content.router, prefix="/api/site-content", tags=["Site Content"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(education.router, prefix="/api/education", tags=["BSF Education"])
