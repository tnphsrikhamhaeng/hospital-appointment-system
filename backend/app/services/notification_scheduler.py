from __future__ import annotations

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.enums import NotificationTypeEnum
from app.repositories.appointment_repository import AppointmentRepository
from app.services.notification_service import NotificationService


BANGKOK_TZ = ZoneInfo("Asia/Bangkok")


def run_reminder_3_days(
    db: Session,
    now: datetime | None = None,
) -> None:
    if now is None:
        now = datetime.now(BANGKOK_TZ)

    target_date = now.date() + timedelta(days=3)

    target_start = datetime.combine(
        target_date,
        time.min,
        tzinfo=BANGKOK_TZ,
    )

    target_end = target_start + timedelta(days=1)

    appointment_repository = AppointmentRepository(db)
    notification_service = NotificationService(db)

    appointments = (
        appointment_repository.get_confirmed_appointments_between(
            start_datetime=target_start,
            end_datetime=target_end,
        )
    )

    for appointment in appointments:
        appointment_datetime = datetime.combine(
            appointment.appointment_date,
            appointment.start_time,
            tzinfo=BANGKOK_TZ,
        )

        notification_service.create_reminder_if_needed(
            appointment=appointment,
            notification_type=NotificationTypeEnum.REMINDER_3_DAYS,
            title="เตือนการนัดหมาย",
            body=(
                "คุณมีนัดหมายในอีก 3 วัน "
                f"{_format_appointment_datetime(appointment_datetime)}"
            ),
        )

    db.commit()


def run_reminder_1_day(
    db: Session,
    now: datetime | None = None,
) -> None:
    if now is None:
        now = datetime.now(BANGKOK_TZ)

    target_date = now.date() + timedelta(days=1)

    target_start = datetime.combine(
        target_date,
        time.min,
        tzinfo=BANGKOK_TZ,
    )

    target_end = target_start + timedelta(days=1)

    appointment_repository = AppointmentRepository(db)
    notification_service = NotificationService(db)

    appointments = (
        appointment_repository.get_confirmed_appointments_between(
            start_datetime=target_start,
            end_datetime=target_end,
        )
    )

    for appointment in appointments:
        appointment_datetime = datetime.combine(
            appointment.appointment_date,
            appointment.start_time,
            tzinfo=BANGKOK_TZ,
        )

        notification_service.create_reminder_if_needed(
            appointment=appointment,
            notification_type=NotificationTypeEnum.REMINDER_1_DAY,
            title="เตือนการนัดหมาย",
            body=(
                "คุณมีนัดหมายในวันพรุ่งนี้ "
                f"{_format_appointment_datetime(appointment_datetime)}"
            ),
        )

    db.commit()


def run_reminder_30_minutes(
    db: Session,
    now: datetime | None = None,
) -> None:
    if now is None:
        now = datetime.now(BANGKOK_TZ)

    target_start = now + timedelta(minutes=30)
    target_end = target_start + timedelta(minutes=1)

    appointment_repository = AppointmentRepository(db)
    notification_service = NotificationService(db)

    appointments = (
        appointment_repository.get_confirmed_appointments_between(
            start_datetime=target_start,
            end_datetime=target_end,
        )
    )

    for appointment in appointments:
        appointment_datetime = datetime.combine(
            appointment.appointment_date,
            appointment.start_time,
            tzinfo=BANGKOK_TZ,
        )

        notification_service.create_reminder_if_needed(
            appointment=appointment,
            notification_type=NotificationTypeEnum.REMINDER_30_MINUTES,
            title="เตือนการนัดหมาย",
            body=(
                "คุณมีนัดหมายในอีก 30 นาที "
                f"{_format_appointment_datetime(appointment_datetime)}"
            ),
        )

    db.commit()


def _format_appointment_datetime(
    appointment_datetime: datetime,
) -> str:
    thai_months = [
        "ม.ค.",
        "ก.พ.",
        "มี.ค.",
        "เม.ย.",
        "พ.ค.",
        "มิ.ย.",
        "ก.ค.",
        "ส.ค.",
        "ก.ย.",
        "ต.ค.",
        "พ.ย.",
        "ธ.ค.",
    ]

    day = appointment_datetime.day
    month = thai_months[appointment_datetime.month - 1]
    year = appointment_datetime.year + 543
    appointment_time = appointment_datetime.strftime("%H:%M")

    return (
        f"วันที่ {day} {month} {year} "
        f"เวลา {appointment_time} น."
    )