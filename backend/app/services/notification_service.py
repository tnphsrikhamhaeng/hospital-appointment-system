from __future__ import annotations

import logging
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
from app.repositories.notification_setting_repository import (
    NotificationSettingRepository,
)
from app.utils.onesignal import send_notification


logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

        self.notification_repository = NotificationRepository(db)

        self.appointment_repository = AppointmentRepository(db)

        self.notification_setting_repository = (
            NotificationSettingRepository(db)
        )

    def _is_notification_enabled(
        self,
        *,
        patient_id: uuid.UUID,
        notification_type: NotificationTypeEnum,
    ) -> bool:

        setting = (
            self.notification_setting_repository
            .get_by_user_id(patient_id)
        )

        if setting is None:
            return True

        appointment_notification_types = {
            NotificationTypeEnum.APPOINTMENT_CONFIRMED,
            NotificationTypeEnum.APPOINTMENT_CHECKED_IN,
            NotificationTypeEnum.REMINDER_3_DAYS,
            NotificationTypeEnum.REMINDER_1_DAY,
            NotificationTypeEnum.REMINDER_30_MINUTES,
            NotificationTypeEnum.READY_FOR_CONSULTATION,
            NotificationTypeEnum.CONSULTATION_DELAYED,
            NotificationTypeEnum.APPOINTMENT_CANCELLED,
            NotificationTypeEnum.APPOINTMENT_RESCHEDULED,
        }

        if notification_type in appointment_notification_types:
            return setting.appointment_notifications

        if (
            notification_type
            == NotificationTypeEnum.MEDICAL_RECORD_CREATED
        ):
            return setting.medical_record_notifications

        if (
            notification_type
            == NotificationTypeEnum.SYSTEM_ANNOUNCEMENT
        ):
            return setting.system_notifications

        return True

    def create_notification(
        self,
        *,
        appointment_id: uuid.UUID,
        patient_id: uuid.UUID,
        notification_type: NotificationTypeEnum,
        title: str,
        body: str,
    ) -> NotificationLog | None:

        if not self._is_notification_enabled(
            patient_id=patient_id,
            notification_type=notification_type,
        ):
            logger.info(
                "Notification disabled by user settings. "
                "user_id=%s notification_type=%s",
                patient_id,
                notification_type,
            )

            return None

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

        try:
            response = send_notification(
                external_id=str(patient_id),
                title=title,
                body=body,
            )

            logger.info(
                "OneSignal notification sent successfully. "
                "user_id=%s response=%s",
                patient_id,
                response,
            )

        except Exception as exc:
            logger.exception(
                "OneSignal notification failed. "
                "user_id=%s error=%s",
                patient_id,
                exc,
            )

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
            self.notification_repository
            .exists_by_appointment_and_type(
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
    ) -> NotificationLog | None:

        notification = (
            self.notification_repository
            .get_by_appointment_and_type(
                appointment_id=appointment.id,
                notification_type=(
                    NotificationTypeEnum.CONSULTATION_DELAYED
                ),
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
            notification_type=(
                NotificationTypeEnum.CONSULTATION_DELAYED
            ),
            title="การตรวจล่าช้า",
            body=(
                "การตรวจของคุณล่าช้ากว่ากำหนด "
                f"{appointment_datetime}"
            ),
        )

    def create_system_notification(
        self,
        *,
        patient_id: uuid.UUID,
        title: str,
        body: str,
    ) -> NotificationLog | None:

        if not self._is_notification_enabled(
            patient_id=patient_id,
            notification_type=(
                NotificationTypeEnum.SYSTEM_ANNOUNCEMENT
            ),
        ):
            logger.info(
                "System notification disabled by user settings. "
                "user_id=%s",
                patient_id,
            )

            return None

        notification = NotificationLog(
            appointment_id=None,
            patient_id=patient_id,
            notification_type=(
                NotificationTypeEnum.SYSTEM_ANNOUNCEMENT
            ),
            notification_status=NotificationStatusEnum.SENT,
            title=title,
            body=body,
            sent_at=datetime.now(timezone.utc),
        )

        notification = self.notification_repository.create(
            notification,
        )

        try:
            response = send_notification(
                external_id=str(patient_id),
                title=title,
                body=body,
            )

            logger.info(
                "System notification sent successfully. "
                "user_id=%s response=%s",
                patient_id,
                response,
            )

        except Exception as exc:
            logger.exception(
                "System notification failed. "
                "user_id=%s error=%s",
                patient_id,
                exc,
            )

        return notification

    def get_patient_notifications(
        self,
        patient_id: uuid.UUID,
    ) -> list[NotificationLog]:

        return self.notification_repository.get_by_patient_id(
            patient_id,
        )

    def clear_patient_notifications(
        self,
        patient_id: uuid.UUID,
    ) -> int:

        deleted_count = (
            self.notification_repository
            .delete_by_patient_id(
                patient_id,
            )
        )

        self.db.commit()

        return deleted_count

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

        if (
            notification.notification_status
            != NotificationStatusEnum.READ
        ):
            notification.notification_status = (
                NotificationStatusEnum.READ
            )

            notification.read_at = (
                datetime.now(timezone.utc)
            )

            self.notification_repository.update(
                notification,
            )

        return notification