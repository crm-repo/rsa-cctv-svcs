from app.models.page import AboutPageResponse, ContactPageBundleResponse, ServicesPageResponse
from app.services.about_service import get_public_about
from app.services.contact_us_service import get_public_contact_page
from app.services.project_gallery_service import list_public_project_gallery
from app.services.service_service import list_public_services


def get_about_page() -> AboutPageResponse:
    return AboutPageResponse(
        about=get_public_about(),
        project_gallery=list_public_project_gallery(),
    )


def get_contact_page() -> ContactPageBundleResponse:
    contact_page = get_public_contact_page()
    return ContactPageBundleResponse(
        company_contact=contact_page.company_contact,
        contact_persons=contact_page.contact_persons,
        social_media=contact_page.social_media,
    )


def get_services_page() -> ServicesPageResponse:
    services = list_public_services()
    return ServicesPageResponse(services=services, total=len(services))
