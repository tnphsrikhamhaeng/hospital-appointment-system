from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.enums import (
    AppointmentStatusEnum,
    NotificationStatusEnum,
    NotificationTypeEnum,
)
from app.core.exceptions import NotFoundException
from app.models.appointment import Appointment
from app.models.notification_log import NotificationLog
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.notification_repository import NotificationRepository
from app.utils.fcm import send_notification
from app.services.user_device_service import UserDeviceService


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_repository = NotificationRepository(db)
        self.appointment_repository = AppointmentRepository(db)
        self.user_device_service = UserDeviceService(db)

    def create_notification(
        self,
        *,
        appointment_id: uuid.UUID,
        patient_id: uuid.UUID,
        notification_type,
        title: str,
        body: str,
    ) -> NotificationLog:
        notification = NotificationLog(
            appointment_id=appointment_id,
            patient_id=patient_id,
            notification_type=notification_type,
            notification_status=NotificationStatusEnum.SENT,
            title=title,
            body=body,
            sent_at=datetime.now(timezone.utc),
        )

        notification = self.notification_repository.create(
            notification,
        )

        devices = self.user_device_service.get_active_devices(
            patient_id,
        )

        for device in devices:
            try:
                send_notification(
                    device_token=device.device_token,
                    title=title,
                    body=body,
                )
            except Exception:
                continue

        return notification

    def create_reminder_if_needed(
        self,
        appointment: Appointment,
        notification_type: NotificationTypeEnum,
        title: str,
        body: str,
    ) -> NotificationLog | None:

        if appointment.status != AppointmentStatusEnum.CONFIRMED:
            return None

        exists = (
            self.notification_repository.exists_by_appointment_and_type(
                appointment_id=appointment.id,
                notification_type=notification_type,
            )
        )

        if exists:
            return None

        return self.create_notification(
            appointment_id=appointment.id,
            patient_id=appointment.patient_id,
            notification_type=notification_type,
            title=title,
            body=body,
        )

    def create_consultation_delayed_notification(
        self,
        appointment: Appointment,
    ) -> NotificationLog:

        notification = (
            self.notification_repository.get_by_appointment_and_type(
                appointment_id=appointment.id,
                notification_type=NotificationTypeEnum.CONSULTATION_DELAYED,
            )
        )

        if notification is not None:
            return notification

        appointment_datetime = (
            appointment.appointment_date.strftime("%d/%m/%Y")
            + " เวลา "
            + appointment.start_time.strftime("%H:%M")
            + " น."
        )

        return self.create_notification(
            appointment_id=appointment.id,
            patient_id=appointment.patient_id,
            notification_type=NotificationTypeEnum.CONSULTATION_DELAYED,
            title="การตรวจล่าช้า",
            body=(
                "การตรวจของคุณล่าช้ากว่ากำหนด "
                f"{appointment_datetime}"
            ),
        )

    def get_patient_notifications(
        self,
        patient_id: uuid.UUID,
    ) -> list[NotificationLog]:
        return self.notification_repository.get_by_patient_id(
            patient_id,
        )

    def get_notification(
        self,
        notification_id: uuid.UUID,
    ) -> NotificationLog:
        notification = self.notification_repository.get_by_id(
            notification_id,
        )

        if notification is None:
            raise NotFoundException(
                detail="Notification not found.",
            )

        return notification

    def mark_as_read(
        self,
        notification_id: uuid.UUID,
    ) -> NotificationLog:
        notification = self.get_notification(
            notification_id,
        )

        if notification.notification_status != NotificationStatusEnum.READ:
            notification.notification_status = (
                NotificationStatusEnum.READ
            )
            notification.read_at = datetime.now(timezone.utc)

            self.notification_repository.update(
                notification,
            )

        return notification