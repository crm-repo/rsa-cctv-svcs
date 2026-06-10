from datetime import datetime, timezone

from app.models.project_gallery import ProjectGalleryItem

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


def list_public_project_gallery() -> list[ProjectGalleryItem]:
    visible_items = [item for item in MOCK_PROJECT_GALLERY if item.show_flag == "Y"]
    return sorted(visible_items, key=lambda item: item.display_seq)
