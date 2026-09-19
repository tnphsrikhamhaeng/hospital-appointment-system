from __future__ import annotations

import uuid

from app.models.notification_setting import NotificationSetting
from app.repositories.notification_setting_repository import (
    NotificationSettingRepository,
)


class NotificationSettingService:
    def __init__(self, db):
        self.db = db
        self.notification_setting_repository = (
            NotificationSettingRepository(db)
        )

    def get_or_create_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> NotificationSetting:
        setting = (
            self.notification_setting_repository.get_by_user_id(
                user_id,
            )
        )

        if setting is not None:
            return setting

        setting = NotificationSetting(
            user_id=user_id,
            all_notifications=True,
            appointment_notifications=True,
            medical_record_notifications=True,
            system_notifications=True,
        )

        setting = self.notification_setting_repository.create(
            setting,
        )

        self.db.commit()

        return setting

    def update_by_user_id(
        self,
        *,
        user_id: uuid.UUID,
        all_notifications: bool,
        appointment_notifications: bool,
        medical_record_notifications: bool,
        system_notifications: bool,
    ) -> NotificationSetting:
        setting = (
            self.notification_setting_repository.get_by_user_id(
                user_id,
            )
        )

        if setting is None:
            setting = NotificationSetting(
                user_id=user_id,
            )

            setting = (
                self.notification_setting_repository.create(
                    setting,
                )
            )

        setting.all_notifications = all_notifications
        setting.appointment_notifications = appointment_notifications
        setting.medical_record_notifications = (
            medical_record_notifications
        )
        setting.system_notifications = system_notifications

        setting = self.notification_setting_repository.update(
            setting,
        )

        self.db.commit()

        return setting