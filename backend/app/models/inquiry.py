import re
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


InquiryStatus = Literal["New", "Replied", "Closed"]


class InquiryCreate(BaseModel):
    product_id: Optional[str] = Field(default=None, max_length=80)

    customer_name: str = Field(min_length=2, max_length=160)
    contact_number: str = Field(min_length=5, max_length=40)
    email: Optional[str] = Field(default=None, max_length=160)

    subject: Optional[str] = Field(default=None, max_length=200)
    message: Optional[str] = Field(default=None, max_length=2000)
    source_page: Optional[str] = Field(default=None, max_length=80)

    @field_validator("contact_number")
    @classmethod
    def validate_contact_number(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not re.fullmatch(r"[0-9+\-\s()]+", cleaned_value):
            raise ValueError("Contact number may only contain numbers, spaces, +, -, and parentheses.")

        return cleaned_value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value.strip() == "":
            return None

        cleaned_value = value.strip()

        if "@" not in cleaned_value or "." not in cleaned_value.split("@")[-1]:
            raise ValueError("Enter a valid email address.")

        return cleaned_value


class InquiryUpdate(BaseModel):
    assigned_person: Optional[str] = Field(default=None, max_length=160)
    status: Optional[InquiryStatus] = None


class Inquiry(BaseModel):
    inquiry_id: str
    customer_id: Optional[str] = None
    product_id: Optional[str] = None

    customer_name: str
    contact_number: str
    email: Optional[str] = None

    subject: Optional[str] = None
    message: Optional[str] = None
    source_page: Optional[str] = None

    assigned_person: Optional[str] = None
    status: InquiryStatus = "New"

    created_at: datetime
    updated_at: datetime


class InquiryListResponse(BaseModel):
    items: list[Inquiry]
    total: int
