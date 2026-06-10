from app.repositories.id_counter_repository import get_next_number

ID_NUMBER_WIDTH = 7


def generate_id(id_prefix: str) -> str:
    """Generate approved Phase 8 v5 ID format: XXXX-0000001."""
    normalized_prefix = id_prefix.strip().upper()

    if not normalized_prefix:
        raise ValueError("ID prefix is required.")

    next_number = get_next_number(normalized_prefix)
    return f"{normalized_prefix}-{next_number:0{ID_NUMBER_WIDTH}d}"


def generate_customer_id() -> str:
    return generate_id("CUST")


def generate_booking_id() -> str:
    return generate_id("BOOK")


def generate_inquiry_id() -> str:
    return generate_id("INQR")


def generate_brand_id() -> str:
    return generate_id("BRND")


def generate_category_id() -> str:
    return generate_id("CATG")


def generate_key_feature_id() -> str:
    return generate_id("KFEA")


def generate_about_id() -> str:
    return generate_id("ABOU")


def generate_project_id() -> str:
    return generate_id("PROJ")


def generate_service_id() -> str:
    return generate_id("SERV")


def generate_contact_company_id() -> str:
    return generate_id("CONT")


def generate_contact_person_id() -> str:
    return generate_id("CPER")


def generate_social_media_id() -> str:
    return generate_id("SOCM")


def generate_product_id_for_category(category_prefix: str) -> str:
    """Generate a product ID from rsa_categories.category_prefix.

    Examples:
    - CCTV -> CCTV-0000001
    - RECO -> RECO-0000001
    - PACK -> PACK-0000001
    """
    return generate_id(category_prefix)
