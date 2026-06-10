from datetime import datetime, timezone
from typing import Optional

from app.models.service import Service

now = datetime.now(timezone.utc)

MOCK_SERVICES: list[Service] = [
    Service(
        service_id="SERV-0000001",
        show_flag="Y",
        display_seq=1,
        service_title="CCTV Installation",
        service_slug="cctv-installation",
        short_description="Professional CCTV installation for homes, shops, offices, and small businesses.",
        service_description="We provide CCTV camera installation with practical camera placement, clean cabling, recorder setup, and mobile-view configuration.",
        image_path="/assets/images/services/cctv-installation.jpg",
        icon_path="/assets/images/icons/cctv-installation.svg",
        cta_label="Request Site Visit",
        cta_url="booking.html",
        meta_title="CCTV Installation Services",
        meta_description="Professional CCTV installation services for residential and commercial customers.",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    Service(
        service_id="SERV-0000002",
        show_flag="Y",
        display_seq=2,
        service_title="CCTV Maintenance",
        service_slug="cctv-maintenance",
        short_description="Maintenance support to keep CCTV systems recording and working properly.",
        service_description="We help inspect cameras, recording equipment, cabling, storage, and remote viewing setup to keep CCTV systems reliable.",
        image_path="/assets/images/services/cctv-maintenance.jpg",
        icon_path="/assets/images/icons/cctv-maintenance.svg",
        cta_label="Book Maintenance",
        cta_url="booking.html",
        meta_title="CCTV Maintenance Services",
        meta_description="CCTV maintenance and support for homes and businesses.",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    Service(
        service_id="SERV-0000003",
        show_flag="Y",
        display_seq=3,
        service_title="Repair and Troubleshooting",
        service_slug="repair-troubleshooting",
        short_description="Troubleshooting for camera, recorder, image, storage, and remote-viewing issues.",
        service_description="We assist with common CCTV issues such as no display, offline cameras, recording problems, weak images, or mobile app access issues.",
        image_path="/assets/images/services/repair-troubleshooting.jpg",
        icon_path="/assets/images/icons/repair.svg",
        cta_label="Get Support",
        cta_url="contact-us.html",
        meta_title="CCTV Repair and Troubleshooting",
        meta_description="CCTV repair and troubleshooting support for camera and recorder issues.",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    Service(
        service_id="SERV-0000004",
        show_flag="N",
        display_seq=99,
        service_title="Hidden Draft Service",
        service_slug="hidden-draft-service",
        short_description="Hidden service should not appear publicly.",
        service_description="This hidden service is for show_flag testing only.",
        image_path="/assets/images/services/hidden.jpg",
        icon_path=None,
        cta_label=None,
        cta_url=None,
        meta_title=None,
        meta_description=None,
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
]


def list_public_services() -> list[Service]:
    visible_services = [service for service in MOCK_SERVICES if service.show_flag == "Y"]
    return sorted(visible_services, key=lambda service: service.display_seq)


def get_public_service_by_slug(service_slug: str) -> Optional[Service]:
    normalized_slug = service_slug.strip().lower()
    for service in MOCK_SERVICES:
        if service.show_flag == "Y" and service.service_slug.lower() == normalized_slug:
            return service
    return None
