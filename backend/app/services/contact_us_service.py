from datetime import datetime, timezone
from typing import Optional

from app.models.contact_us import ContactPageResponse, ContactUsRecord
from app.repositories.repository_factory import create_contact_us_repository

now = datetime.now(timezone.utc)

MOCK_CONTACT_US_RECORDS: list[ContactUsRecord] = [
    ContactUsRecord(
        contact_us_id="CONT-0000001",
        show_flag="Y",
        contact_type="Company Contact",
        display_seq=1,
        primary_contact_number="+63 919 123 4567",
        secondary_contact_number="+63 917 654 3210",
        company_email="info@rsacctv.example.com",
        company_address="123 RSA Office Street, Metro Manila, Philippines",
        showroom_address="456 RSA Showroom Avenue, Metro Manila, Philippines",
        whatsapp_number="+63 919 123 4567",
        viber_number="+63 917 654 3210",
        business_hours="Monday to Saturday, 9:00 AM to 6:00 PM",
        office_map_embed_url="https://maps.example.com/embed/office",
        office_map_link_url="https://maps.example.com/office",
        showroom_map_embed_url="https://maps.example.com/embed/showroom",
        showroom_map_link_url="https://maps.example.com/showroom",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    ContactUsRecord(
        contact_us_id="CPER-0000001",
        show_flag="Y",
        contact_type="Contact Person",
        display_seq=1,
        person_image_path="/assets/images/contact/person-sales.jpg",
        person_name="RSA Sales Team",
        position_title="Sales and Site Visit Coordinator",
        department="Sales",
        phone_number="+63 919 123 4567",
        email_address="sales@rsacctv.example.com",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    ContactUsRecord(
        contact_us_id="CPER-0000002",
        show_flag="Y",
        contact_type="Contact Person",
        display_seq=2,
        person_image_path="/assets/images/contact/person-support.jpg",
        person_name="RSA Support Team",
        position_title="Technical Support Coordinator",
        department="Support",
        phone_number="+63 917 654 3210",
        email_address="support@rsacctv.example.com",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    ContactUsRecord(
        contact_us_id="CPER-0000003",
        show_flag="N",
        contact_type="Contact Person",
        display_seq=99,
        person_image_path="/assets/images/contact/hidden-person.jpg",
        person_name="Hidden Contact Person",
        position_title="Hidden Draft Contact",
        department="Draft",
        phone_number="+63 900 000 0000",
        email_address="hidden@rsacctv.example.com",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    ContactUsRecord(
        contact_us_id="SOCM-0000001",
        show_flag="Y",
        contact_type="Social Media",
        display_seq=1,
        platform_name="Facebook",
        platform_key="facebook",
        profile_url="https://facebook.com/rsacctv",
        icon_code="fa-brands fa-facebook-f",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    ContactUsRecord(
        contact_us_id="SOCM-0000002",
        show_flag="Y",
        contact_type="Social Media",
        display_seq=2,
        platform_name="Instagram",
        platform_key="instagram",
        profile_url="https://instagram.com/rsacctv",
        icon_code="fa-brands fa-instagram",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    ContactUsRecord(
        contact_us_id="SOCM-0000003",
        show_flag="Y",
        contact_type="Social Media",
        display_seq=3,
        platform_name="WhatsApp",
        platform_key="whatsapp",
        profile_url="https://wa.me/639191234567",
        icon_code="fa-brands fa-whatsapp",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    ContactUsRecord(
        contact_us_id="SOCM-0000004",
        show_flag="Y",
        contact_type="Social Media",
        display_seq=4,
        platform_name="YouTube",
        platform_key="youtube",
        profile_url="https://youtube.com/@rsacctv",
        icon_code="fa-brands fa-youtube",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    ContactUsRecord(
        contact_us_id="SOCM-0000005",
        show_flag="N",
        contact_type="Social Media",
        display_seq=99,
        platform_name="Hidden Social",
        platform_key="hidden",
        profile_url="https://example.com/hidden",
        icon_code="fa-solid fa-eye-slash",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
]


def _get_contact_us_repository():
    return create_contact_us_repository(initial_items=MOCK_CONTACT_US_RECORDS)


def list_public_contact_records() -> list[ContactUsRecord]:
    records = _get_contact_us_repository().list_visible()
    return sorted(records, key=lambda record: (record.contact_type, record.display_seq))


def get_public_company_contact() -> Optional[ContactUsRecord]:
    return _get_contact_us_repository().get_visible_company_contact()


def list_public_contact_persons() -> list[ContactUsRecord]:
    return _get_contact_us_repository().list_visible_by_type("Contact Person")


def list_public_social_media() -> list[ContactUsRecord]:
    return _get_contact_us_repository().list_visible_by_type("Social Media")


def get_public_contact_page() -> ContactPageResponse:
    return ContactPageResponse(
        company_contact=get_public_company_contact(),
        contact_persons=list_public_contact_persons(),
        social_media=list_public_social_media(),
    )


# --- Batch 21 admin CMS CRUD helpers ---
from typing import Any

from app.models.contact_us import ContactUsRecordListResponse
from app.services.id_service import generate_contact_company_id, generate_contact_person_id, generate_social_media_id


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text_value = str(value).strip()
    return text_value or None


def _contact_id_for_type(contact_type: str) -> str:
    if contact_type == "Company Contact":
        return generate_contact_company_id()
    if contact_type == "Contact Person":
        return generate_contact_person_id()
    if contact_type == "Social Media":
        return generate_social_media_id()
    raise ValueError("Invalid contact_type.")


def list_admin_contact_records(search: Optional[str] = None, contact_type: Optional[str] = None) -> ContactUsRecordListResponse:
    records = _get_contact_us_repository().list_all()
    if contact_type:
        key = contact_type.strip().lower()
        records = [record for record in records if record.contact_type.lower() == key]
    if search:
        query = search.strip().lower()
        records = [record for record in records if query in " ".join(str(value or "") for value in record.model_dump().values()).lower()]
    records.sort(key=lambda record: (record.contact_type, record.display_seq, record.contact_us_id))
    return ContactUsRecordListResponse(items=records, total=len(records))


def get_admin_contact_record_by_id(contact_us_id: str) -> Optional[ContactUsRecord]:
    return _get_contact_us_repository().get_by_id(contact_us_id)


def create_admin_contact_record(request) -> ContactUsRecord:
    repository = _get_contact_us_repository()
    data = request.model_dump()
    contact_type = data.get("contact_type")
    if not contact_type:
        raise ValueError("contact_type is required.")
    now = _now_utc()
    record_data = {key: _clean_text(value) if isinstance(value, str) else value for key, value in data.items() if key != "updated_by"}
    record = ContactUsRecord(
        **record_data,
        contact_us_id=_contact_id_for_type(contact_type),
        created_at=now,
        updated_at=now,
        created_by=_clean_text(data.get("updated_by")) or "admin",
        updated_by=_clean_text(data.get("updated_by")) or "admin",
    )
    return repository.save_contact_record(record)


def update_admin_contact_record(contact_us_id: str, request) -> Optional[ContactUsRecord]:
    repository = _get_contact_us_repository()
    existing = repository.get_by_id(contact_us_id)
    if existing is None:
        return None
    data = existing.model_dump(mode="python")
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key != "updated_by":
            data[key] = _clean_text(value) if isinstance(value, str) else value
    data["updated_at"] = _now_utc()
    data["updated_by"] = _clean_text(update_data.get("updated_by")) or "admin"
    record = ContactUsRecord.model_validate(data)
    return repository.save_contact_record(record)
