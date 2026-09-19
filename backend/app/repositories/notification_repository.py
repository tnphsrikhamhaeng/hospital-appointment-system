from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification_log import NotificationLog


class NotificationRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        notification: NotificationLog,
    ) -> NotificationLog:
        self.db.add(notification)
        self.db.flush()

        return notification

    def update(
        self,
        notification: NotificationLog,
    ) -> NotificationLog:
        self.db.flush()

        return notification

    def get_by_id(
        self,
        notification_id: uuid.UUID,
    ) -> NotificationLog | None:
        statement = select(NotificationLog).where(
            NotificationLog.id == notification_id,
        )

        return self.db.scalar(statement)

    def get_by_appointment_id(
        self,
        appointment_id: uuid.UUID,
    ) -> list[NotificationLog]:
        statement = (
            select(NotificationLog)
            .where(
                NotificationLog.appointment_id == appointment_id,
            )
            .order_by(
                NotificationLog.created_at.desc(),
            )
        )

        return list(
            self.db.scalars(statement).all(),
        )

    def get_by_appointment_and_type(
        self,
        appointment_id: uuid.UUID,
        notification_type,
    ) -> NotificationLog | None:
        statement = select(NotificationLog).where(
            NotificationLog.appointment_id == appointment_id,
            NotificationLog.notification_type == notification_type,
        )

        return self.db.scalar(statement)

    def exists_by_appointment_and_type(
        self,
        appointment_id: uuid.UUID,
        notification_type,
    ) -> bool:
        statement = select(NotificationLog.id).where(
            NotificationLog.appointment_id == appointment_id,
            NotificationLog.notification_type == notification_type,
        )

        return self.db.scalar(statement) is not None

    def get_by_patient_id(
        self,
        patient_id: uuid.UUID,
    ) -> list[NotificationLog]:
        statement = (
            select(NotificationLog)
            .where(
                NotificationLog.patient_id == patient_id,
            )
            .order_by(
                NotificationLog.created_at.desc(),
            )
        )

        return list(
            self.db.scalars(statement).all(),
        )