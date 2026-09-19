from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_device import UserDevice


class UserDeviceRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        user_device: UserDevice,
    ) -> UserDevice:
        self.db.add(user_device)
        self.db.flush()

        return user_device

    def get_by_device_token(
        self,
        device_token: str,
    ) -> UserDevice | None:
        statement = select(UserDevice).where(
            UserDevice.device_token == device_token,
        )

        return self.db.scalar(statement)

    def get_active_devices_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> list[UserDevice]:
        statement = select(UserDevice).where(
            UserDevice.user_id == user_id,
            UserDevice.is_active.is_(True),
        )

        return list(
            self.db.scalars(statement).all(),
        )

    def update(
        self,
        user_device: UserDevice,
    ) -> UserDevice:
        self.db.flush()

        return user_device
      
    def get_by_id(
        self,
        device_id: uuid.UUID,
    ) -> UserDevice | None:
        statement = select(UserDevice).where(
            UserDevice.id == device_id,
        )

        return self.db.scalar(statement)