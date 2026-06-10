from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


ContactType = Literal["Company Contact", "Contact Person", "Social Media"]


class ContactUsRecord(BaseModel):
    contact_us_id: str
    show_flag: str = Field(pattern="^(Y|N)$")
    contact_type: ContactType
    display_seq: int = 0

    # Company Contact fields
    primary_contact_number: Optional[str] = None
    secondary_contact_number: Optional[str] = None
    company_email: Optional[str] = None
    company_address: Optional[str] = None
    showroom_address: Optional[str] = None
    whatsapp_number: Optional[str] = None
    viber_number: Optional[str] = None
    business_hours: Optional[str] = None
    office_map_embed_url: Optional[str] = None
    office_map_link_url: Optional[str] = None
    showroom_map_embed_url: Optional[str] = None
    showroom_map_link_url: Optional[str] = None

    # Contact Person fields
    person_image_path: Optional[str] = None
    person_name: Optional[str] = None
    position_title: Optional[str] = None
    department: Optional[str] = None
    phone_number: Optional[str] = None
    email_address: Optional[str] = None

    # Social Media fields
    platform_name: Optional[str] = None
    platform_key: Optional[str] = None
    profile_url: Optional[str] = None
    icon_code: Optional[str] = None

    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class ContactUsRecordListResponse(BaseModel):
    items: list[ContactUsRecord]
    total: int


class ContactPageResponse(BaseModel):
    company_contact: Optional[ContactUsRecord] = None
    contact_persons: list[ContactUsRecord] = Field(default_factory=list)
    social_media: list[ContactUsRecord] = Field(default_factory=list)
