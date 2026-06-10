"""Reusable normalization helpers for lead/customer matching."""

from typing import Optional


def normalize_contact_number(contact_number: str) -> str:
    """Normalize phone/contact number for matching and future GSI lookup.

    Keeps numbers/text safe as strings; removes common spacing/punctuation.
    This mirrors the approved customer matching rule for
    contact_number_normalized-index.
    """

    return (
        contact_number.strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )


def normalize_email(email_address: Optional[str]) -> Optional[str]:
    if email_address is None or email_address.strip() == "":
        return None
    return email_address.strip().lower()


def clean_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None
