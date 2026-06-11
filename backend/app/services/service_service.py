from datetime import datetime, timezone
from typing import Optional

from app.models.service import Service
from app.repositories.repository_factory import create_service_repository

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


def _get_service_repository():
    return create_service_repository(initial_items=MOCK_SERVICES)


def list_public_services() -> list[Service]:
    return _get_service_repository().list_visible_sorted()


def get_public_service_by_slug(service_slug: str) -> Optional[Service]:
    return _get_service_repository().get_visible_by_slug(service_slug)


# --- Batch 21 admin CMS CRUD helpers ---
import re
from typing import Any

from app.services.id_service import generate_service_id


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "service"


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text_value = str(value).strip()
    return text_value or None


def list_admin_services(search: Optional[str] = None) -> list[Service]:
    services = _get_service_repository().list_all()
    if search:
        query = search.strip().lower()
        services = [service for service in services if query in service.service_id.lower() or query in service.service_title.lower() or query in service.service_slug.lower() or query in service.short_description.lower()]
    services.sort(key=lambda service: (service.display_seq, service.service_title.lower()))
    return services


def get_admin_service_by_id(service_id: str) -> Optional[Service]:
    return _get_service_repository().get_by_id(service_id)


def create_admin_service(request) -> Service:
    repository = _get_service_repository()
    data = request.model_dump()
    now = _now_utc()
    title = _clean_text(data.get("service_title"))
    short_description = _clean_text(data.get("short_description"))
    if not title:
        raise ValueError("Service title is required.")
    if not short_description:
        raise ValueError("Short description is required.")
    slug = _clean_text(data.get("service_slug")) or _slugify(title)
    service = Service(
        service_id=generate_service_id(),
        show_flag=data.get("show_flag") or "Y",
        display_seq=int(data.get("display_seq") or 0),
        service_title=title,
        service_slug=slug,
        short_description=short_description,
        service_description=_clean_text(data.get("service_description")),
        image_path=_clean_text(data.get("image_path")),
        icon_path=_clean_text(data.get("icon_path")),
        cta_label=_clean_text(data.get("cta_label")),
        cta_url=_clean_text(data.get("cta_url")),
        meta_title=_clean_text(data.get("meta_title")) or title,
        meta_description=_clean_text(data.get("meta_description")),
        created_at=now,
        updated_at=now,
        created_by=_clean_text(data.get("updated_by")) or "admin",
        updated_by=_clean_text(data.get("updated_by")) or "admin",
    )
    return repository.save_service(service)


def update_admin_service(service_id: str, request) -> Optional[Service]:
    repository = _get_service_repository()
    existing = repository.get_by_id(service_id)
    if existing is None:
        return None
    data = existing.model_dump(mode="python")
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key != "updated_by":
            data[key] = value
    if data.get("service_title") and not data.get("service_slug"):
        data["service_slug"] = _slugify(data["service_title"])
    data["updated_at"] = _now_utc()
    data["updated_by"] = _clean_text(update_data.get("updated_by")) or "admin"
    service = Service.model_validate(data)
    return repository.save_service(service)
