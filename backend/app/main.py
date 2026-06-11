from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import (
    about,
    admin_auth,
    bookings,
    brands,
    categories,
    contact_us,
    customers,
    health,
    inquiries,
    key_features,
    package_banners,
    pages,
    products,
    project_gallery,
    services,
)

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Backend API for RSA CMS / Mini-CRM",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "RSA CMS API is running",
        "status": "ok",
    }


app.include_router(health.router, prefix=settings.API_PREFIX, tags=["Health"])
app.include_router(admin_auth.router, prefix=settings.API_PREFIX, tags=["Admin Auth"])
app.include_router(products.router, prefix=settings.API_PREFIX, tags=["Products"])
app.include_router(brands.router, prefix=settings.API_PREFIX, tags=["Brands"])
app.include_router(categories.router, prefix=settings.API_PREFIX, tags=["Categories"])
app.include_router(key_features.router, prefix=settings.API_PREFIX, tags=["Key Features"])
app.include_router(package_banners.router, prefix=settings.API_PREFIX, tags=["Package Banners"])
app.include_router(about.router, prefix=settings.API_PREFIX, tags=["About"])
app.include_router(project_gallery.router, prefix=settings.API_PREFIX, tags=["Project Gallery"])
app.include_router(services.router, prefix=settings.API_PREFIX, tags=["Services"])
app.include_router(contact_us.router, prefix=settings.API_PREFIX, tags=["Contact Us"])
app.include_router(pages.router, prefix=settings.API_PREFIX, tags=["Pages"])
app.include_router(bookings.router, prefix=settings.API_PREFIX, tags=["Bookings"])
app.include_router(inquiries.router, prefix=settings.API_PREFIX, tags=["Inquiries"])
app.include_router(customers.router, prefix=settings.API_PREFIX, tags=["Customers"])
