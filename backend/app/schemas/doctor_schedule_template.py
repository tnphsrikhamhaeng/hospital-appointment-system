from __future__ import annotations

import uuid
from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, model_validator

from app.core.enums import WeekdayEnum


class DoctorScheduleTemplateCreateRequest(BaseModel):
    doctor_id: uuid.UUID

    weekday: WeekdayEnum

    start_time: time

    end_time: time

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.start_time >= self.end_time:
            raise ValueError(
                "Start time must be earlier than end time.",
            )

        return self


class DoctorScheduleTemplateUpdateRequest(BaseModel):
    weekday: WeekdayEnum | None = None

    start_time: time | None = None

    end_time: time | None = None

    is_active: bool | None = None

    @model_validator(mode="after")
    def validate_time_range(self):
        if (
            self.start_time is not None
            and self.end_time is not None
            and self.start_time >= self.end_time
        ):
            raise ValueError(
                "Start time must be earlier than end time.",
            )

        return self


class DoctorScheduleTemplateResponse(BaseModel):
    id: uuid.UUID

    doctor_id: uuid.UUID

    weekday: WeekdayEnum

    start_time: time

    end_time: time

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )