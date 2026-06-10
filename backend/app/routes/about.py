from fastapi import APIRouter, HTTPException

from app.models.about import About
from app.services.about_service import get_public_about

router = APIRouter()


@router.get("/about", response_model=About)
def get_about():
    about = get_public_about()
    if about is None:
        raise HTTPException(status_code=404, detail="About content not found")
    return about
