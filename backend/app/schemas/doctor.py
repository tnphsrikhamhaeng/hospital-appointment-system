from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    field_validator,
)

from app.core.enums import DoctorPrefaceEnum, DoctorStatusEnum
from app.core.regex import LICENSE_NUMBER_PATTERN, NAME_PATTERN, PHONE_PATTERN
from app.core.validators import normalize_name
from app.schemas.department import DepartmentResponse
from app.schemas.specialization import SpecializationResponse


class DoctorCreateRequest(BaseModel):
    employee_id: str = Field(
        min_length=1,
        max_length=20,
    )

    password: str = Field(
        min_length=8,
        max_length=255,
    )

    profile_image_url: HttpUrl | None = None

    preface: DoctorPrefaceEnum

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

    license_number: str = Field(
        pattern=LICENSE_NUMBER_PATTERN,
    )

    phone_number: str = Field(
        pattern=PHONE_PATTERN,
    )

    email: EmailStr

    department_id: uuid.UUID

    specialization_ids: list[uuid.UUID] = Field(
        ...,
        min_length=1,
    )

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def normalize_names(cls, value: str) -> str:
        return normalize_name(value)

    model_config = ConfigDict(
        extra="forbid",
    )


class DoctorUpdateRequest(BaseModel):
    profile_image_url: HttpUrl | None = None

    first_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
        pattern=NAME_PATTERN,
    )

    last_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
        pattern=NAME_PATTERN,
    )

    phone_number: str | None = Field(
        default=None,
        pattern=PHONE_PATTERN,
    )

    email: EmailStr | None = None

    status: DoctorStatusEnum | None = None

    department_id: uuid.UUID | None = None

    specialization_ids: list[uuid.UUID] | None = None

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def normalize_names(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_name(value)

    model_config = ConfigDict(
        extra="forbid",
    )


class DoctorDeactivateRequest(BaseModel):
    password: str = Field(
        min_length=1,
        max_length=255,
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class DoctorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

    profile_image_url: HttpUrl | None

    preface: DoctorPrefaceEnum

    first_name: str

    last_name: str

    license_number: str

    phone_number: str

    email: EmailStr

    status: DoctorStatusEnum

    department: DepartmentResponse

    specializations: list[SpecializationResponse]

    created_at: datetime

    updated_at: datetime