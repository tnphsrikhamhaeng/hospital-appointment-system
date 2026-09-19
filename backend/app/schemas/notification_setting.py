from __future__ import annotations

from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict


class NotificationSettingResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    all_notifications: bool
    appointment_notifications: bool
    medical_record_notifications: bool
    system_notifications: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationSettingUpdateRequest(BaseModel):
    all_notifications: bool
    appointment_notifications: bool
    medical_record_notifications: bool
    system_notifications: bool