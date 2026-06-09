from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "rsa-cms-api",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "phase": "Phase 8 - Backend / Admin CMS / Mini-CRM",
    }