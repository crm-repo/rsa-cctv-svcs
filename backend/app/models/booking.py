import re
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


BookingStatus = Literal["New", "Contacted", "Scheduled", "Completed", "Cancelled"]


class BookingCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=160)
    contact_number: str = Field(min_length=5, max_length=40)
    email: Optional[str] = Field(default=None, max_length=160)

    address: Optional[str] = Field(default=None, max_length=500)
    preferred_date: Optional[date] = None
    preferred_time: Optional[str] = Field(default=None, max_length=40)
    service_interest: Optional[str] = Field(default=None, max_length=160)
    notes: Optional[str] = Field(default=None, max_length=2000)

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

    @field_validator("preferred_date")
    @classmethod
    def validate_preferred_date(cls, value: Optional[date]) -> Optional[date]:
        if value is not None and value < date.today():
            raise ValueError("Preferred date cannot be in the past.")

        return value


class BookingUpdate(BaseModel):
    booking_type: Optional[str] = Field(default=None, max_length=80)
    assigned_person: Optional[str] = Field(default=None, max_length=160)
    comments: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[BookingStatus] = None


class Booking(BaseModel):
    booking_id: str
    customer_id: Optional[str] = None

    customer_name: str
    contact_number: str
    email: Optional[str] = None

    address: Optional[str] = None
    preferred_date: Optional[date] = None
    preferred_time: Optional[str] = None
    service_interest: Optional[str] = None
    notes: Optional[str] = None

    booking_type: str = "Site Visit Request"
    assigned_person: Optional[str] = None
    comments: Optional[str] = None

    status: BookingStatus = "New"

    created_at: datetime
    updated_at: datetime


class BookingListResponse(BaseModel):
    items: list[Booking]
    total: int
