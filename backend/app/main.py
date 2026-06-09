from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

from app.routes import brands, health, products

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
app.include_router(products.router, prefix=settings.API_PREFIX, tags=["Products"])
app.include_router(brands.router, prefix=settings.API_PREFIX, tags=["Brands"])