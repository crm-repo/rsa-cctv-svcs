from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Customer(BaseModel):
    customer_id: str

    customer_name: str = Field(min_length=2, max_length=160)
    customer_status: Literal["Active", "Prospect", "Inactive"] = "Prospect"
    customer_category: Optional[Literal["Residential", "Commercial"]] = None

    email_address: Optional[str] = Field(default=None, max_length=160)
    contact_number: str = Field(min_length=5, max_length=40)

    customer_from: Literal[
        "Inquiries",
        "Booking Request",
        "Social Media",
        "Referral",
        "Others",
        "Walk-In",
        "Phone Call",
        "Email",
    ]

    sales_person: Optional[str] = None
    repeat_customer: str = Field(default="N", pattern="^(Y|N)$")

    created_at: datetime
    updated_at: datetime


class CustomerListResponse(BaseModel):
    items: list[Customer]
    total: int
