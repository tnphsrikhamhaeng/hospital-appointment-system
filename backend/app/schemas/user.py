from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.enums import (
    GenderEnum,
    UserRoleEnum,
    UserStatusEnum,
)
from app.core.regex import (
    NAME_PATTERN,
    PHONE_PATTERN,
)


class UpdateProfileRequest(BaseModel):
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

    email: EmailStr | None = Field(
        default=None,
    )

    model_config = ConfigDict(extra="forbid")


class ProfileResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: str
    gender: GenderEnum | None
    date_of_birth: date | None
    role: UserRoleEnum
    status: UserStatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(ProfileResponse):
    pass