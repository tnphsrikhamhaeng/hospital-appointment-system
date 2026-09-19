from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.notification_setting import (
    NotificationSettingResponse,
    NotificationSettingUpdateRequest,
)
from app.services.notification_setting_service import (
    NotificationSettingService,
)


router = APIRouter(
    prefix="/notification-settings",
    tags=["Notification Settings"],
)


def get_notification_setting_service(
    db: Session = Depends(get_db),
) -> NotificationSettingService:
    return NotificationSettingService(db)


@router.get(
    "/users/{user_id}",
    response_model=NotificationSettingResponse,
)
def get_notification_settings(
    user_id: uuid.UUID,
    service: NotificationSettingService = Depends(
        get_notification_setting_service,
    ),
):
    return service.get_or_create_by_user_id(user_id)


@router.patch(
    "/users/{user_id}",
    response_model=NotificationSettingResponse,
)
def update_notification_settings(
    user_id: uuid.UUID,
    request: NotificationSettingUpdateRequest,
    service: NotificationSettingService = Depends(
        get_notification_setting_service,
    ),
):
    return service.update_by_user_id(
        user_id=user_id,
        all_notifications=request.all_notifications,
        appointment_notifications=request.appointment_notifications,
        medical_record_notifications=request.medical_record_notifications,
        system_notifications=request.system_notifications,
    )