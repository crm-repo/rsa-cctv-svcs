from datetime import datetime, timezone
from typing import Optional

from app.models.about import About
from app.repositories.repository_factory import create_about_repository

now = datetime.now(timezone.utc)

MOCK_ABOUT_RECORDS: list[About] = [
    About(
        about_id="ABOU-0000001",
        show_flag="Y",
        hero_title="Trusted CCTV Installation and Security Solutions",
        hero_subtitle="R.S.A. CCTV Installation Services provides reliable CCTV installation, maintenance, and security system support for homes and businesses.",
        hero_image_path="/assets/images/about/about-hero.jpg",
        company_story_title="Our Company Story",
        company_story_body="R.S.A. CCTV Installation Services helps customers protect what matters through practical CCTV solutions, professional installation, and after-sales support.",
        company_story_image_path="/assets/images/about/company-story.jpg",
        mission_title="Our Mission",
        mission_body="To provide dependable and affordable CCTV solutions with honest advice, quality products, and reliable installation support.",
        vision_title="Our Vision",
        vision_body="To become a trusted local CCTV and security partner for residential and commercial customers.",
        why_choose_title="Why Choose R.S.A.",
        why_choose_body="We focus on practical security recommendations, clean installation, and responsive support.",
        why_choose_bullet_01="Experienced CCTV installation support",
        why_choose_bullet_02="Trusted security brands and products",
        why_choose_bullet_03="Residential and commercial solutions",
        why_choose_bullet_04="After-sales guidance and support",
        why_choose_bullet_05="Affordable CCTV packages",
        why_choose_bullet_06="Customer-focused service",
        meta_title="About R.S.A. CCTV Installation Services",
        meta_description="Learn more about R.S.A. CCTV Installation Services and our CCTV installation, maintenance, and security solutions.",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    )
]


def _get_about_repository():
    return create_about_repository(initial_items=MOCK_ABOUT_RECORDS)


def get_public_about() -> Optional[About]:
    return _get_about_repository().get_visible_about()


# --- Batch 21 admin CMS CRUD helpers ---
from typing import Any

from app.models.about import AboutListResponse
from app.services.id_service import generate_about_id


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text_value = str(value).strip()
    return text_value or None


def _request_update_data(request: Any) -> dict[str, Any]:
    return request.model_dump(exclude_unset=True)


def list_admin_about() -> AboutListResponse:
    items = _get_about_repository().list_all()
    items.sort(key=lambda item: item.about_id)
    return AboutListResponse(items=items, total=len(items))


def get_admin_about_by_id(about_id: str) -> Optional[About]:
    return _get_about_repository().get_by_id(about_id)


def create_admin_about(request) -> About:
    repository = _get_about_repository()
    data = request.model_dump()
    now = _now_utc()
    about = About(
        about_id=generate_about_id(),
        show_flag=data.get("show_flag") or "Y",
        hero_title=_clean_text(data.get("hero_title")) or "About RSA CCTV",
        hero_subtitle=_clean_text(data.get("hero_subtitle")),
        hero_image_path=_clean_text(data.get("hero_image_path")),
        company_story_title=_clean_text(data.get("company_story_title")),
        company_story_body=_clean_text(data.get("company_story_body")),
        company_story_image_path=_clean_text(data.get("company_story_image_path")),
        mission_title=_clean_text(data.get("mission_title")),
        mission_body=_clean_text(data.get("mission_body")),
        vision_title=_clean_text(data.get("vision_title")),
        vision_body=_clean_text(data.get("vision_body")),
        why_choose_title=_clean_text(data.get("why_choose_title")),
        why_choose_body=_clean_text(data.get("why_choose_body")),
        why_choose_bullet_01=_clean_text(data.get("why_choose_bullet_01")),
        why_choose_bullet_02=_clean_text(data.get("why_choose_bullet_02")),
        why_choose_bullet_03=_clean_text(data.get("why_choose_bullet_03")),
        why_choose_bullet_04=_clean_text(data.get("why_choose_bullet_04")),
        why_choose_bullet_05=_clean_text(data.get("why_choose_bullet_05")),
        why_choose_bullet_06=_clean_text(data.get("why_choose_bullet_06")),
        meta_title=_clean_text(data.get("meta_title")),
        meta_description=_clean_text(data.get("meta_description")),
        created_at=now,
        updated_at=now,
        created_by=_clean_text(data.get("updated_by")) or "admin",
        updated_by=_clean_text(data.get("updated_by")) or "admin",
    )
    return repository.save_about(about)


def update_admin_about(about_id: str, request) -> Optional[About]:
    repository = _get_about_repository()
    existing = repository.get_by_id(about_id)
    if existing is None:
        return None
    data = existing.model_dump(mode="python")
    update_data = _request_update_data(request)
    for key, value in update_data.items():
        if key != "updated_by":
            data[key] = value
    data["updated_at"] = _now_utc()
    data["updated_by"] = _clean_text(update_data.get("updated_by")) or "admin"
    about = About.model_validate(data)
    return repository.save_about(about)
