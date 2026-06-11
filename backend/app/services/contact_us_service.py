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
