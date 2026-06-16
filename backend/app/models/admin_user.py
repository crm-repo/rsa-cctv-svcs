from __future__ import annotations

from pydantic import BaseModel, Field


class AdminUser(BaseModel):
    username: str
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    role: str = "Standard"
    groups: list[str] = Field(default_factory=list)
    status: str = ""
    enabled: bool = True
    password_status: str = ""
    created_at: str = ""
    updated_at: str = ""


class AdminUserListResponse(BaseModel):
    items: list[AdminUser]
    count: int
    roles: list[str] = Field(default_factory=lambda: ["Admin", "Standard"])


class AdminUserCreateRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=80)
    last_name: str = Field(..., min_length=1, max_length=80)
    email: str = Field(..., min_length=3, max_length=160)
    role: str = Field(default="Standard", pattern="^(Admin|Standard)$")


class AdminUserUpdateRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=80)
    last_name: str = Field(..., min_length=1, max_length=80)
    role: str = Field(default="Standard", pattern="^(Admin|Standard)$")
    enabled: bool | None = None


class AdminUserCreateResponse(BaseModel):
    user: AdminUser
    temporary_password: str
    message: str


class AdminUserResetPasswordResponse(BaseModel):
    username: str
    temporary_password: str
    message: str


class AdminUserActionResponse(BaseModel):
    user: AdminUser
    message: str
