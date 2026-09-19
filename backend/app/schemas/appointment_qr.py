from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AppointmentQRCodeResponse(BaseModel):
    token: str
    expired_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AppointmentQRCodeCheckInRequest(BaseModel):
    token: str


class AppointmentQRCodeCheckInResponse(BaseModel):
    message: str


class AppointmentQRCodeStaffCheckInPreviewResponse(BaseModel):
    appointment_id: UUID

    patient_name: str

    appointment_date: date
    start_time: time
    end_time: time

    doctor_name: str

    department_name: str


class AppointmentQRCodeModelResponse(BaseModel):
    id: UUID
    appointment_id: UUID
    token: str
    expired_at: datetime
    is_used: bool
    used_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)