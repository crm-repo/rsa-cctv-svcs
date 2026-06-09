from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import health

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