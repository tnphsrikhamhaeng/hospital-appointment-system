from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import (
    NotificationStatusEnum,
    NotificationTypeEnum,
)


class NotificationResponse(BaseModel):
    id: uuid.UUID

    appointment_id: uuid.UUID
    patient_id: uuid.UUID

    notification_type: NotificationTypeEnum
    notification_status: NotificationStatusEnum

    title: str
    body: str

    sent_at: datetime | None
    read_at: datetime | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )