from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import date, datetime
from app.core.regex import NAME_PATTERN, PHONE_PATTERN
from app.core.validators import normalize_name

import uuid


class StaffCreateRequest(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=50,
    )

    password: str = Field(
        min_length=8,
        max_length=255,
    )

    first_name: str = Field(
        min_length=2,
        max_length=50,
        pattern=NAME_PATTERN,
    )

    last_name: str = Field(
        min_length=2,
        max_length=50,
        pattern=NAME_PATTERN,
    )

    phone_number: str = Field(
        pattern=PHONE_PATTERN,
    )

    email: EmailStr

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def normalize_names(cls, value: str) -> str:
        return normalize_name(value)

    model_config = ConfigDict(
        extra="forbid",
    )

class StaffListResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: str
    gender: str | None
    date_of_birth: date | None
    role: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
    
class StaffUpdateRequest(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=50,
    )

    first_name: str = Field(
        min_length=2,
        max_length=50,
        pattern=NAME_PATTERN,
    )

    last_name: str = Field(
        min_length=2,
        max_length=50,
        pattern=NAME_PATTERN,
    )

    phone_number: str = Field(
        pattern=PHONE_PATTERN,
    )

    email: EmailStr

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def normalize_names(cls, value: str) -> str:
        return normalize_name(value)

    model_config = ConfigDict(
        extra="forbid",
    )
    
class StaffDeactivateRequest(BaseModel):
    password: str = Field(
        min_length=1,
        description="Staff password for staff deactivation",
    )