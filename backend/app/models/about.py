from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class About(BaseModel):
    about_id: str
    show_flag: str = Field(pattern="^(Y|N)$")

    hero_title: str
    hero_subtitle: Optional[str] = None
    hero_image_path: Optional[str] = None

    company_story_title: Optional[str] = None
    company_story_body: Optional[str] = None
    company_story_image_path: Optional[str] = None

    mission_title: Optional[str] = None
    mission_body: Optional[str] = None

    vision_title: Optional[str] = None
    vision_body: Optional[str] = None

    why_choose_title: Optional[str] = None
    why_choose_body: Optional[str] = None
    why_choose_bullet_01: Optional[str] = None
    why_choose_bullet_02: Optional[str] = None
    why_choose_bullet_03: Optional[str] = None
    why_choose_bullet_04: Optional[str] = None
    why_choose_bullet_05: Optional[str] = None
    why_choose_bullet_06: Optional[str] = None

    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class AboutListResponse(BaseModel):
    items: list[About]
    total: int


class AboutAdminCreateRequest(BaseModel):
    show_flag: str = Field(default="Y", pattern="^(Y|N)$")
    hero_title: str
    hero_subtitle: Optional[str] = None
    hero_image_path: Optional[str] = None
    company_story_title: Optional[str] = None
    company_story_body: Optional[str] = None
    company_story_image_path: Optional[str] = None
    mission_title: Optional[str] = None
    mission_body: Optional[str] = None
    vision_title: Optional[str] = None
    vision_body: Optional[str] = None
    why_choose_title: Optional[str] = None
    why_choose_body: Optional[str] = None
    why_choose_bullet_01: Optional[str] = None
    why_choose_bullet_02: Optional[str] = None
    why_choose_bullet_03: Optional[str] = None
    why_choose_bullet_04: Optional[str] = None
    why_choose_bullet_05: Optional[str] = None
    why_choose_bullet_06: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    updated_by: Optional[str] = "admin"


class AboutAdminUpdateRequest(BaseModel):
    show_flag: Optional[str] = Field(default=None, pattern="^(Y|N)$")
    hero_title: Optional[str] = None
    hero_subtitle: Optional[str] = None
    hero_image_path: Optional[str] = None
    company_story_title: Optional[str] = None
    company_story_body: Optional[str] = None
    company_story_image_path: Optional[str] = None
    mission_title: Optional[str] = None
    mission_body: Optional[str] = None
    vision_title: Optional[str] = None
    vision_body: Optional[str] = None
    why_choose_title: Optional[str] = None
    why_choose_body: Optional[str] = None
    why_choose_bullet_01: Optional[str] = None
    why_choose_bullet_02: Optional[str] = None
    why_choose_bullet_03: Optional[str] = None
    why_choose_bullet_04: Optional[str] = None
    why_choose_bullet_05: Optional[str] = None
    why_choose_bullet_06: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    updated_by: Optional[str] = "admin"
