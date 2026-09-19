from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import DevicePlatformEnum


class UserDeviceRegisterRequest(BaseModel):
    device_token: str = Field(
        min_length=1,
        max_length=512,
    )

    platform: DevicePlatformEnum

    device_name: str | None = Field(
        default=None,
        max_length=255,
    )


class UserDeviceResponse(BaseModel):
    id: uuid.UUID

    platform: DevicePlatformEnum

    device_name: str | None

    is_active: bool

    last_used_at: datetime

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )