"""Reusable normalization helpers for lead/customer matching."""

import re
from typing import Optional


def normalize_contact_number(contact_number: str) -> str:
    """Normalize phone/contact number for matching and future GSI lookup.

    Phase 8 launch uses Philippine mobile numbers for customer matching.
    The normalized value is digits only and stores equivalent Philippine mobile
    formats in one canonical international form without the plus sign.

    Examples:
        +63 919 123 4567  -> 639191234567
        0919 123 4567     -> 639191234567
        (0) 919 123 4567  -> 639191234567
        919 123 4567      -> 639191234567

    Non-Philippine / non-mobile values fall back to digits-only normalization
    so the helper remains safe for office numbers or older sample records.
    """

    if contact_number is None:
        return ""

    digits = re.sub(r"\D+", "", contact_number.strip())

    if not digits:
        return ""

    # International prefix entered as 0063 919 123 4567.
    if len(digits) == 14 and digits.startswith("00639"):
        return digits[2:]

    # Philippine mobile in international format without punctuation.
    if len(digits) == 12 and digits.startswith("639"):
        return digits

    # Some users write international format with a local trunk zero:
    # +63 (0) 919 123 4567 -> 6309191234567.
    if len(digits) == 13 and digits.startswith("6309"):
        return "63" + digits[3:]

    # Philippine local mobile format: 0919 123 4567.
    if len(digits) == 11 and digits.startswith("09"):
        return "63" + digits[1:]

    # Philippine mobile without leading zero/country code: 919 123 4567.
    if len(digits) == 10 and digits.startswith("9"):
        return "63" + digits

    return digits


def normalize_email(email_address: Optional[str]) -> Optional[str]:
    if email_address is None or email_address.strip() == "":
        return None
    return email_address.strip().lower()


def clean_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None
