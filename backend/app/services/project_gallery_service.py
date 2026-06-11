from datetime import datetime, timezone

from app.models.project_gallery import ProjectGalleryItem
from app.repositories.repository_factory import create_project_gallery_repository

now = datetime.now(timezone.utc)

MOCK_PROJECT_GALLERY: list[ProjectGalleryItem] = [
    ProjectGalleryItem(
        project_id="PROJ-0000001",
        show_flag="Y",
        display_seq=1,
        project_title="Residential CCTV Installation",
        project_description="Home CCTV setup with outdoor cameras and mobile viewing support.",
        image_path="/assets/images/projects/residential-cctv.jpg",
        alt_text="Residential CCTV camera installation project",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    ProjectGalleryItem(
        project_id="PROJ-0000002",
        show_flag="Y",
        display_seq=2,
        project_title="Small Business CCTV Setup",
        project_description="Security camera coverage for shopfront and indoor monitoring.",
        image_path="/assets/images/projects/business-cctv.jpg",
        alt_text="Small business CCTV setup project",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    ProjectGalleryItem(
        project_id="PROJ-0000003",
        show_flag="Y",
        display_seq=3,
        project_title="Warehouse Camera Coverage",
        project_description="Camera placement for wider area visibility and recording coverage.",
        image_path="/assets/images/projects/warehouse-cctv.jpg",
        alt_text="Warehouse CCTV camera coverage project",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    ProjectGalleryItem(
        project_id="PROJ-0000004",
        show_flag="N",
        display_seq=99,
        project_title="Hidden Draft Gallery Item",
        project_description="This hidden gallery item should not appear publicly.",
        image_path="/assets/images/projects/hidden.jpg",
        alt_text="Hidden project gallery item",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
]


def _get_project_gallery_repository():
    return create_project_gallery_repository(initial_items=MOCK_PROJECT_GALLERY)


def list_public_project_gallery() -> list[ProjectGalleryItem]:
    return _get_project_gallery_repository().list_visible_sorted()


# --- Batch 21 admin CMS CRUD helpers ---
from typing import Any, Optional

from app.models.project_gallery import ProjectGalleryListResponse
from app.services.id_service import generate_project_id


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text_value = str(value).strip()
    return text_value or None


def list_admin_project_gallery(search: Optional[str] = None) -> ProjectGalleryListResponse:
    items = _get_project_gallery_repository().list_all()
    if search:
        query = search.strip().lower()
        items = [item for item in items if query in item.project_id.lower() or query in item.project_title.lower() or (item.project_description and query in item.project_description.lower())]
    items.sort(key=lambda item: (item.display_seq, item.project_title.lower()))
    return ProjectGalleryListResponse(items=items, total=len(items))


def get_admin_project_by_id(project_id: str) -> Optional[ProjectGalleryItem]:
    return _get_project_gallery_repository().get_by_id(project_id)


def create_admin_project(request) -> ProjectGalleryItem:
    repository = _get_project_gallery_repository()
    data = request.model_dump()
    now = _now_utc()
    title = _clean_text(data.get("project_title"))
    image_path = _clean_text(data.get("image_path"))
    if not title:
        raise ValueError("Project title is required.")
    if not image_path:
        raise ValueError("Image path is required.")
    project = ProjectGalleryItem(
        project_id=generate_project_id(),
        show_flag=data.get("show_flag") or "Y",
        display_seq=int(data.get("display_seq") or 0),
        project_title=title,
        project_description=_clean_text(data.get("project_description")),
        image_path=image_path,
        alt_text=_clean_text(data.get("alt_text")),
        created_at=now,
        updated_at=now,
        created_by=_clean_text(data.get("updated_by")) or "admin",
        updated_by=_clean_text(data.get("updated_by")) or "admin",
    )
    return repository.save_project(project)


def update_admin_project(project_id: str, request) -> Optional[ProjectGalleryItem]:
    repository = _get_project_gallery_repository()
    existing = repository.get_by_id(project_id)
    if existing is None:
        return None
    data = existing.model_dump(mode="python")
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key != "updated_by":
            data[key] = value
    data["updated_at"] = _now_utc()
    data["updated_by"] = _clean_text(update_data.get("updated_by")) or "admin"
    project = ProjectGalleryItem.model_validate(data)
    return repository.save_project(project)
