from datetime import datetime, timezone
from typing import Optional

from app.models.about import About

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


def get_public_about() -> Optional[About]:
    for about in MOCK_ABOUT_RECORDS:
        if about.show_flag == "Y":
            return about
    return None
