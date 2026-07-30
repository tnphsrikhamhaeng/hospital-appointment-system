from __future__ import annotations

import uuid
from datetime import date

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.core.enums import GenderEnum
from app.core.regex import (
    NAME_PATTERN,
    PHONE_PATTERN,
    USERNAME_PATTERN,
)
from app.core.validators import (
    normalize_username,
    validate_date_of_birth,
    validate_password_strength,
)


class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=4,
        max_length=20,
        pattern=USERNAME_PATTERN,
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

    date_of_birth: date

    gender: GenderEnum

    phone_number: str = Field(
        pattern=PHONE_PATTERN,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=20,
    )

    confirm_password: str = Field(
        min_length=8,
        max_length=20,
    )

    model_config = ConfigDict(
        extra="forbid",
    )

    @field_validator("username", mode="before")
    @classmethod
    def username_validator(cls, value: str) -> str:
        return normalize_username(value)

    @field_validator("date_of_birth")
    @classmethod
    def date_of_birth_validator(cls, value: date) -> date:
        return validate_date_of_birth(value)

    @field_validator("password")
    @classmethod
    def password_validator(cls, value: str) -> str:
        return validate_password_strength(value)

    @model_validator(mode="after")
    def validate_password_match(self) -> "RegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Password mismatch")
        return self


class RegisterResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    message: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class LoginRequest(BaseModel):
    username: str = Field(
        min_length=4,
        max_length=20,
    )

    password: str = Field(
        min_length=8,
        max_length=20,
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(
        from_attributes=True,
    )