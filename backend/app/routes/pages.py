from fastapi import APIRouter

from app.models.page import AboutPageResponse, ContactPageBundleResponse, ServicesPageResponse
from app.services.page_service import get_about_page, get_contact_page, get_services_page

router = APIRouter()


@router.get("/pages/about", response_model=AboutPageResponse)
def get_page_about():
    return get_about_page()


@router.get("/pages/contact", response_model=ContactPageBundleResponse)
def get_page_contact():
    return get_contact_page()


@router.get("/pages/services", response_model=ServicesPageResponse)
def get_page_services():
    return get_services_page()
