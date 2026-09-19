from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.notification_setting import NotificationSetting


class NotificationSettingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> NotificationSetting | None:
        return (
            self.db.query(NotificationSetting)
            .filter(NotificationSetting.user_id == user_id)
            .first()
        )

    def create(
        self,
        setting: NotificationSetting,
    ) -> NotificationSetting:
        self.db.add(setting)
        self.db.flush()
        return setting

    def update(
        self,
        setting: NotificationSetting,
    ) -> NotificationSetting:
        self.db.flush()
        return setting