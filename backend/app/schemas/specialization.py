from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import SpecializationStatusEnum
from app.core.validators import normalize_name


class SpecializationBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        description="Specialization name",
    )

    description: str | None = Field(
        default=None,
        max_length=500,
        description="Specialization description",
    )

    department_id: UUID

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = normalize_name(value)

        if not value:
            raise ValueError("Specialization name cannot be empty.")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = normalize_name(value)

        return value or None


class SpecializationCreateRequest(SpecializationBase):
    model_config = ConfigDict(
    extra="forbid"
)
    pass


class SpecializationUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    department_id: UUID | None = None

    status: SpecializationStatusEnum | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = normalize_name(value)

        if not value:
            raise ValueError("Specialization name cannot be empty.")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = normalize_name(value)

        return value or None
    
    model_config = ConfigDict(
    extra="forbid"
)


class SpecializationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    department_id: UUID
    status: SpecializationStatusEnum
    created_at: datetime
    updated_at: datetime
