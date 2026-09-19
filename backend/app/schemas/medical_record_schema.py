from __future__ import annotations

import uuid
from datetime import date, datetime, time

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class MedicalRecordBase(BaseModel):
    chief_complaint: str = Field(
        min_length=1,
    )

    present_illness: str | None = Field(
        default=None,
    )

    physical_examination: str | None = Field(
        default=None,
    )

    diagnosis: str = Field(
        min_length=1,
    )

    treatment: str | None = Field(
        default=None,
    )

    recommendation: str | None = Field(
        default=None,
    )

    note: str | None = Field(
        default=None,
    )


class MedicalRecordCreate(MedicalRecordBase):
    appointment_id: uuid.UUID


class MedicalRecordUpdate(BaseModel):
    chief_complaint: str | None = Field(
        default=None,
        min_length=1,
    )

    present_illness: str | None = Field(
        default=None,
    )

    physical_examination: str | None = Field(
        default=None,
    )

    diagnosis: str | None = Field(
        default=None,
        min_length=1,
    )

    treatment: str | None = Field(
        default=None,
    )

    recommendation: str | None = Field(
        default=None,
    )

    note: str | None = Field(
        default=None,
    )


class MedicalRecordResponse(MedicalRecordBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: uuid.UUID
    appointment_id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class DoctorMedicalHistoryResponse(BaseModel):
    appointment_id: uuid.UUID
    appointment_date: date
    start_time: time
    end_time: time
    patient_id: uuid.UUID
    patient_name: str
    status: str
    medical_record: MedicalRecordResponse | None = None