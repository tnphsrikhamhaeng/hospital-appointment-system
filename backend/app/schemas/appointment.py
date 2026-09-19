from __future__ import annotations

import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import AppointmentStatusEnum


class AppointmentCreateRequest(BaseModel):
    doctor_id: uuid.UUID
    appointment_date: date
    start_time: time
    reason: str | None = Field(
        default=None,
        max_length=500,
    )

    @field_validator("appointment_date")
    @classmethod
    def validate_appointment_date(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Appointment date cannot be in the past.")
        return value


class AppointmentCancelRequest(BaseModel):
    cancelled_reason: str = Field(
        min_length=1,
        max_length=500,
    )


class AppointmentRescheduleRequest(BaseModel):
    appointment_date: date
    start_time: time

    @field_validator("appointment_date")
    @classmethod
    def validate_appointment_date(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Appointment date cannot be in the past.")
        return value


class AppointmentStatusUpdateRequest(BaseModel):
    status: AppointmentStatusEnum
    room_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )


class AppointmentResponse(BaseModel):
    id: uuid.UUID

    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    department_id: uuid.UUID

    appointment_date: date
    start_time: time
    end_time: time

    reason: str | None

    status: AppointmentStatusEnum

    cancelled_reason: str | None
    cancelled_at: datetime | None
    confirmed_at: datetime | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DoctorScheduleResponse(BaseModel):
    id: uuid.UUID

    patient_id: uuid.UUID
    patient_name: str

    appointment_date: date
    start_time: time
    end_time: time

    status: AppointmentStatusEnum

    model_config = ConfigDict(from_attributes=True)


class AppointmentSummaryResponse(BaseModel):
    id: uuid.UUID

    doctor_id: uuid.UUID
    department_id: uuid.UUID

    appointment_date: date
    start_time: time
    end_time: time

    status: AppointmentStatusEnum

    model_config = ConfigDict(from_attributes=True)


class AppointmentListResponse(BaseModel):
    appointments: list[AppointmentSummaryResponse]
    total: int