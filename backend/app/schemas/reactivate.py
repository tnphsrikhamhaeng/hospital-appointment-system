from enum import Enum
import uuid

from pydantic import BaseModel, ConfigDict, Field


class ReactivateTargetType(str, Enum):
    DOCTOR = "doctor"
    DEPARTMENT = "department"
    SPECIALIZATION = "specialization"
    STAFF = "staff"


class ReactivateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_type: ReactivateTargetType
    target_id: uuid.UUID
    password: str = Field(min_length=1, max_length=255)