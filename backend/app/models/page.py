from pydantic import BaseModel, Field

from app.models.about import About
from app.models.contact_us import ContactPageResponse
from app.models.project_gallery import ProjectGalleryItem
from app.models.service import Service


class AboutPageResponse(BaseModel):
    about: About | None = None
    project_gallery: list[ProjectGalleryItem] = Field(default_factory=list)


class ServicesPageResponse(BaseModel):
    services: list[Service] = Field(default_factory=list)
    total: int


class ContactPageBundleResponse(ContactPageResponse):
    pass
