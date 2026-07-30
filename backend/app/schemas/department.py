from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import DepartmentStatusEnum
from app.core.validators import normalize_name


class DepartmentBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        description="Department name",
    )

    description: str | None = Field(
        default=None,
        max_length=500,
        description="Department description",
    )
    
    slot_duration_minutes: int = Field(
        ge=5,
        le=120,
        description="Appointment slot duration in minutes",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = normalize_name(value)

        if not value:
            raise ValueError("Department name cannot be empty.")

        return value


class DepartmentCreateRequest(DepartmentBase):
    model_config = ConfigDict(
    extra="forbid"
)
    pass


class DepartmentUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )
    
    slot_duration_minutes: int | None = Field(
        default=None,
        ge=5,
        le=120,
    )

    status: DepartmentStatusEnum | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = normalize_name(value)

        if not value:
            raise ValueError("Department name cannot be empty.")

        return value
    
    model_config = ConfigDict(
    extra="forbid"
)


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    slot_duration_minutes: int
    status: DepartmentStatusEnum
    created_at: datetime
    updated_at: datetime

   