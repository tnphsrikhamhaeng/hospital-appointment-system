import pytest

import uuid

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.enums import AppointmentStatusEnum, UserRoleEnum
from app.models.appointment import Appointment
from app.models.appointment_qr_code import AppointmentQRCode
from app.services.appointment_qr import AppointmentQRCodeService

from app.core.exceptions import (
    CannotGenerateAppointmentQRCodeException,
    AppointmentNotFoundException,
    AppointmentQRCodeNotFoundException,
    AppointmentQRCodeAlreadyUsedException,
    ForbiddenException,
    CannotCheckInCancelledAppointmentException,
    ConflictException,
    AppointmentQRCodeExpiredException
)

from app.schemas.appointment_qr import (
    AppointmentQRCodeCheckInRequest,
)

from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from app.models.user import User


def test_get_qr_success():
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment)
            .outerjoin(
                AppointmentQRCode,
                AppointmentQRCode.appointment_id
                == Appointment.id,
            )
            .where(
                Appointment.status.notin_(
                    [
                        AppointmentStatusEnum.CANCELLED,
                        AppointmentStatusEnum.COMPLETED,
                        AppointmentStatusEnum.NO_SHOW,
                    ]
                ),
                AppointmentQRCode.id.is_(None),
            )
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        if appointment is None:
            pytest.skip(
                "No appointment without QR code available."
            )

        service = AppointmentQRCodeService(db)

        result = service.get_qr(
            appointment.id
        )

        assert result is not None
        assert result.token.startswith("CF-")
        assert len(result.token) == 10
        assert result.expired_at is not None

        saved_qr = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id,
            )
        )

        assert saved_qr is not None
        assert saved_qr.token == result.token
        assert saved_qr.is_used is False

    finally:
        db.rollback()
        db.close()

def test_get_qr_existing_qr_returns_same_token():
    db = SessionLocal()

    try:
        qr_code = db.scalar(
            select(AppointmentQRCode)
            .order_by(
                AppointmentQRCode.created_at.desc()
            )
        )

        if qr_code is None:
            pytest.skip(
                "No existing QR code found."
            )

        appointment = db.get(
            Appointment,
            qr_code.appointment_id,
        )

        if appointment is None:
            pytest.skip(
                "Appointment for QR code not found."
            )

        service = AppointmentQRCodeService(db)

        result = service.get_qr(
            appointment.id
        )

        assert result is not None
        assert result.token == qr_code.token

        qr_codes = db.scalars(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id,
            )
        ).all()

        assert len(qr_codes) == 1

    finally:
        db.rollback()
        db.close()
        
def test_get_qr_rejected_for_invalid_appointment_status():
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment)
            .where(
                Appointment.status.in_(
                    [
                        AppointmentStatusEnum.CANCELLED,
                        AppointmentStatusEnum.COMPLETED,
                        AppointmentStatusEnum.NO_SHOW,
                    ]
                )
            )
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        if appointment is None:
            pytest.skip(
                "No appointment with invalid QR status found."
            )

        existing_qr = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id,
            )
        )

        if existing_qr is not None:
            pytest.skip(
                "Selected appointment already has a QR code."
            )

        service = AppointmentQRCodeService(db)

        with pytest.raises(
            CannotGenerateAppointmentQRCodeException
        ):
            service.get_qr(
                appointment.id
            )

    finally:
        db.rollback()
        db.close()

def test_get_qr_appointment_not_found():
    db = SessionLocal()

    try:
        service = AppointmentQRCodeService(db)

        with pytest.raises(
            AppointmentNotFoundException
        ):
            service.get_qr(uuid.uuid4())

    finally:
        db.rollback()
        db.close()

def test_patient_check_in_with_qr_success():
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment)
            .outerjoin(
                AppointmentQRCode,
                AppointmentQRCode.appointment_id
                == Appointment.id,
            )
            .where(
                Appointment.status
                == AppointmentStatusEnum.CONFIRMED,
                AppointmentQRCode.id.is_(None),
            )
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        if appointment is None:
            pytest.skip(
                "No confirmed appointment without QR code found."
            )

        patient = db.get(
            User,
            appointment.patient_id,
        )

        if patient is None:
            pytest.skip(
                "Patient for appointment not found."
            )

        now = datetime.now(
            ZoneInfo("Asia/Bangkok")
        ).replace(
            second=0,
            microsecond=0,
        )

        # หาเวลาที่สามารถ Check-in ได้
        # และไม่ชนกับ Appointment อื่นของ Doctor คนเดียวกัน
        appointment_start = now + timedelta(minutes=30)

        for _ in range(120):
            conflict = db.scalar(
                select(Appointment)
                .where(
                    Appointment.doctor_id
                    == appointment.doctor_id,
                    Appointment.appointment_date
                    == appointment_start.date(),
                    Appointment.start_time
                    == appointment_start.time(),
                    Appointment.id != appointment.id,
                    Appointment.status.notin_(
                        [
                            AppointmentStatusEnum.CANCELLED,
                            AppointmentStatusEnum.COMPLETED,
                            AppointmentStatusEnum.NO_SHOW,
                        ]
                    ),
                )
            )

            if conflict is None:
                break

            appointment_start += timedelta(minutes=1)
        else:
            pytest.skip(
                "No available appointment time found."
            )

        appointment.appointment_date = (
            appointment_start.date()
        )

        appointment.start_time = (
            appointment_start.time()
        )

        appointment.end_time = (
            appointment_start
            + timedelta(minutes=30)
        ).time()

        db.flush()

        service = AppointmentQRCodeService(db)

        qr_result = service.get_qr(
            appointment.id
        )

        request = AppointmentQRCodeCheckInRequest(
            token=qr_result.token,
        )

        result = service.check_in(
            request=request,
            current_user=patient,
        )

        assert result is not None
        assert result.message == "Check-in successful."

        db.refresh(appointment)

        assert appointment.status == (
            AppointmentStatusEnum.CHECKED_IN
        )

        qr_code = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id,
            )
        )

        assert qr_code is not None
        assert qr_code.token == qr_result.token
        assert qr_code.is_used is True
        assert qr_code.used_at is not None

    finally:
        db.rollback()
        db.close()
        
def test_patient_check_in_invalid_qr_token():
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment)
            .where(
                Appointment.status
                == AppointmentStatusEnum.CONFIRMED,
            )
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        if appointment is None:
            pytest.skip(
                "No confirmed appointment found."
            )

        patient = db.get(
            User,
            appointment.patient_id,
        )

        if patient is None:
            pytest.skip(
                "Patient for appointment not found."
            )

        service = AppointmentQRCodeService(db)

        request = AppointmentQRCodeCheckInRequest(
            token="CF-INVALID-QR",
        )

        with pytest.raises(
            AppointmentQRCodeNotFoundException
        ):
            service.check_in(
                request=request,
                current_user=patient,
            )

    finally:
        db.rollback()
        db.close()

def test_patient_check_in_already_used_qr():
    db = SessionLocal()

    try:
        qr_code = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.is_used.is_(True)
            )
            .order_by(
                AppointmentQRCode.created_at.desc()
            )
        )

        if qr_code is None:
            pytest.skip(
                "No used QR code found."
            )

        appointment = db.get(
            Appointment,
            qr_code.appointment_id,
        )

        if appointment is None:
            pytest.skip(
                "Appointment for QR code not found."
            )

        patient = db.get(
            User,
            appointment.patient_id,
        )

        if patient is None:
            pytest.skip(
                "Patient for appointment not found."
            )

        service = AppointmentQRCodeService(db)

        request = AppointmentQRCodeCheckInRequest(
            token=qr_code.token,
        )

        with pytest.raises(
            AppointmentQRCodeAlreadyUsedException
        ):
            service.check_in(
                request=request,
                current_user=patient,
            )

    finally:
        db.rollback()
        db.close()

def test_patient_check_in_other_patient_qr_forbidden():
    db = SessionLocal()

    try:
        qr_code = db.scalar(
            select(AppointmentQRCode)
            .join(
                Appointment,
                Appointment.id
                == AppointmentQRCode.appointment_id,
            )
            .where(
                AppointmentQRCode.is_used.is_(False)
            )
            .order_by(
                AppointmentQRCode.created_at.desc()
            )
        )

        if qr_code is None:
            pytest.skip(
                "No unused QR code found."
            )

        appointment = db.get(
            Appointment,
            qr_code.appointment_id,
        )

        if appointment is None:
            pytest.skip(
                "Appointment for QR code not found."
            )

        other_patient = db.scalar(
            select(User)
            .where(
                User.role == UserRoleEnum.PATIENT,
                User.id != appointment.patient_id,
            )
        )

        if other_patient is None:
            pytest.skip(
                "No other patient found."
            )

        service = AppointmentQRCodeService(db)

        request = AppointmentQRCodeCheckInRequest(
            token=qr_code.token,
        )

        with pytest.raises(ForbiddenException):
            service.check_in(
                request=request,
                current_user=other_patient,
            )

    finally:
        db.rollback()
        db.close()

def test_patient_check_in_cancelled_appointment():
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment)
            .where(
                Appointment.status
                == AppointmentStatusEnum.CANCELLED,
            )
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        if appointment is None:
            pytest.skip(
                "No cancelled appointment found."
            )

        patient = db.get(
            User,
            appointment.patient_id,
        )

        if patient is None:
            pytest.skip(
                "Patient for appointment not found."
            )

        qr_code = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id,
                AppointmentQRCode.is_used.is_(False),
            )
        )

        if qr_code is None:
            pytest.skip(
                "No unused QR code for cancelled appointment."
            )

        service = AppointmentQRCodeService(db)

        request = AppointmentQRCodeCheckInRequest(
            token=qr_code.token,
        )

        with pytest.raises(
            CannotCheckInCancelledAppointmentException
        ):
            service.check_in(
                request=request,
                current_user=patient,
            )

    finally:
        db.rollback()
        db.close()
        
@pytest.mark.parametrize(
    "appointment_status",
    [
        AppointmentStatusEnum.COMPLETED,
        AppointmentStatusEnum.NO_SHOW,
    ],
)
def test_patient_check_in_completed_or_no_show_appointment(
    appointment_status,
):
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment)
            .where(
                Appointment.status
                == appointment_status,
            )
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        if appointment is None:
            pytest.skip(
                f"No {appointment_status} appointment found."
            )

        patient = db.get(
            User,
            appointment.patient_id,
        )

        if patient is None:
            pytest.skip(
                "Patient for appointment not found."
            )

        qr_code = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id,
                AppointmentQRCode.is_used.is_(False),
            )
        )

        if qr_code is None:
            pytest.skip(
                "No unused QR code for appointment."
            )

        service = AppointmentQRCodeService(db)

        request = AppointmentQRCodeCheckInRequest(
            token=qr_code.token,
        )

        with pytest.raises(
            CannotGenerateAppointmentQRCodeException
        ):
            service.check_in(
                request=request,
                current_user=patient,
            )

    finally:
        db.rollback()
        db.close()

def test_patient_check_in_before_allowed_time():
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment)
            .where(
                Appointment.status
                == AppointmentStatusEnum.CONFIRMED,
            )
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        if appointment is None:
            pytest.skip(
                "No confirmed appointment found."
            )

        patient = db.get(
            User,
            appointment.patient_id,
        )

        if patient is None:
            pytest.skip(
                "Patient for appointment not found."
            )

        qr_code = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id,
                AppointmentQRCode.is_used.is_(False),
            )
        )

        if qr_code is None:
            qr_result = AppointmentQRCodeService(
                db
            ).get_qr(appointment.id)

            token = qr_result.token
        else:
            token = qr_code.token

        now = datetime.now(
            ZoneInfo("Asia/Bangkok")
        )

        appointment_start = (
            now + timedelta(hours=2)
        )

        appointment.appointment_date = (
            appointment_start.date()
        )

        appointment.start_time = (
            appointment_start.time().replace(
                second=0,
                microsecond=0,
            )
        )

        appointment.end_time = (
            appointment_start
            + timedelta(minutes=30)
        ).time().replace(
            second=0,
            microsecond=0,
        )

        db.flush()

        service = AppointmentQRCodeService(db)

        request = AppointmentQRCodeCheckInRequest(
            token=token,
        )

        with pytest.raises(ConflictException):
            service.check_in(
                request=request,
                current_user=patient,
            )

        db.refresh(appointment)

        assert appointment.status == (
            AppointmentStatusEnum.CONFIRMED
        )

    finally:
        db.rollback()
        db.close()
        
def test_patient_check_in_with_expired_qr():
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment)
            .outerjoin(
                AppointmentQRCode,
                AppointmentQRCode.appointment_id
                == Appointment.id,
            )
            .where(
                Appointment.status
                == AppointmentStatusEnum.CONFIRMED,
                AppointmentQRCode.id.is_(None),
            )
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        if appointment is None:
            pytest.skip(
                "No confirmed appointment without QR code found."
            )

        patient = db.get(
            User,
            appointment.patient_id,
        )

        if patient is None:
            pytest.skip(
                "Patient for appointment not found."
            )

        now = datetime.now(
            ZoneInfo("Asia/Bangkok")
        ).replace(
            second=0,
            microsecond=0,
        )

        # QR หมดอายุเมื่อ appointment_start + 15 นาที
        # จึงกำหนด appointment ให้เริ่มย้อนหลัง 30 นาที
        appointment_start = now - timedelta(minutes=30)

        for _ in range(120):
            conflict = db.scalar(
                select(Appointment)
                .where(
                    Appointment.doctor_id
                    == appointment.doctor_id,
                    Appointment.appointment_date
                    == appointment_start.date(),
                    Appointment.start_time
                    == appointment_start.time(),
                    Appointment.id != appointment.id,
                    Appointment.status.notin_(
                        [
                            AppointmentStatusEnum.CANCELLED,
                            AppointmentStatusEnum.COMPLETED,
                            AppointmentStatusEnum.NO_SHOW,
                        ]
                    ),
                )
            )

            if conflict is None:
                break

            appointment_start -= timedelta(minutes=1)
        else:
            pytest.skip(
                "No available appointment time found."
            )

        appointment.appointment_date = (
            appointment_start.date()
        )

        appointment.start_time = (
            appointment_start.time()
        )

        appointment.end_time = (
            appointment_start
            + timedelta(minutes=30)
        ).time()

        db.flush()

        service = AppointmentQRCodeService(db)

        qr_result = service.get_qr(
            appointment.id
        )

        request = AppointmentQRCodeCheckInRequest(
            token=qr_result.token,
        )

        with pytest.raises(
            AppointmentQRCodeExpiredException
        ):
            service.check_in(
                request=request,
                current_user=patient,
            )

        db.refresh(appointment)

        assert appointment.status == (
            AppointmentStatusEnum.NO_SHOW
        )

        qr_code = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id,
            )
        )

        assert qr_code is not None
        assert qr_code.token == qr_result.token
        assert qr_code.is_used is False
        assert qr_code.used_at is None

    finally:
        db.rollback()
        db.close()

def test_staff_check_in_preview_success():
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment)
            .where(
                Appointment.status
                == AppointmentStatusEnum.CONFIRMED,
            )
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        if appointment is None:
            pytest.skip(
                "No confirmed appointment found."
            )

        patient = db.get(
            User,
            appointment.patient_id,
        )

        doctor = db.get(
            User,
            appointment.doctor_id,
        )

        staff = db.scalar(
            select(User)
            .where(
                User.role
                == UserRoleEnum.HOSPITAL_STAFF,
            )
        )

        if patient is None:
            pytest.skip(
                "Patient for appointment not found."
            )

        if doctor is None:
            pytest.skip(
                "Doctor for appointment not found."
            )

        if staff is None:
            pytest.skip(
                "No hospital staff user found."
            )

        service = AppointmentQRCodeService(db)

        qr_result = service.get_qr(
            appointment.id
        )

        request = AppointmentQRCodeCheckInRequest(
            token=qr_result.token,
        )

        result = service.staff_check_in_preview(
            request=request,
            current_user=staff,
        )

        assert result is not None
        assert result.appointment_id == appointment.id
        assert result.patient_name is not None
        assert result.doctor_name is not None
        assert result.department_name is not None
        assert result.appointment_date == (
            appointment.appointment_date
        )
        assert result.start_time == (
            appointment.start_time
        )
        assert result.end_time == (
            appointment.end_time
        )

        db.refresh(appointment)

        # Preview ต้องไม่ Check-in จริง
        assert appointment.status == (
            AppointmentStatusEnum.CONFIRMED
        )

        qr_code = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id,
            )
        )

        assert qr_code is not None
        assert qr_code.is_used is False

    finally:
        db.rollback()
        db.close()

def test_staff_check_in_success():
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment)
            .outerjoin(
                AppointmentQRCode,
                AppointmentQRCode.appointment_id
                == Appointment.id,
            )
            .where(
                Appointment.status
                == AppointmentStatusEnum.CONFIRMED,
                AppointmentQRCode.id.is_(None),
            )
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        if appointment is None:
            pytest.skip(
                "No confirmed appointment without QR code found."
            )

        staff = db.scalar(
            select(User)
            .where(
                User.role
                == UserRoleEnum.HOSPITAL_STAFF,
            )
        )

        if staff is None:
            pytest.skip(
                "No hospital staff user found."
            )

        service = AppointmentQRCodeService(db)

        qr_result = service.get_qr(
            appointment.id
        )

        request = AppointmentQRCodeCheckInRequest(
            token=qr_result.token,
        )

        result = service.staff_check_in(
            request=request,
            current_user=staff,
        )

        assert result is not None
        assert result.message == "Check-in successful."

        db.refresh(appointment)

        assert appointment.status == (
            AppointmentStatusEnum.CHECKED_IN
        )

        qr_code = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id,
            )
        )

        assert qr_code is not None
        assert qr_code.token == qr_result.token
        assert qr_code.is_used is True
        assert qr_code.used_at is not None

    finally:
        db.rollback()
        db.close()

def test_staff_check_in_forbidden_for_non_staff():
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment)
            .where(
                Appointment.status
                == AppointmentStatusEnum.CONFIRMED,
            )
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        if appointment is None:
            pytest.skip(
                "No confirmed appointment found."
            )

        non_staff = db.get(
            User,
            appointment.patient_id,
        )

        if non_staff is None:
            pytest.skip(
                "Patient for appointment not found."
            )

        if non_staff.role == UserRoleEnum.HOSPITAL_STAFF:
            pytest.skip(
                "Selected user is hospital staff."
            )

        service = AppointmentQRCodeService(db)

        qr_result = service.get_qr(
            appointment.id
        )

        request = AppointmentQRCodeCheckInRequest(
            token=qr_result.token,
        )

        with pytest.raises(ForbiddenException):
            service.staff_check_in(
                request=request,
                current_user=non_staff,
            )

        db.refresh(appointment)

        # ต้องไม่เกิด Check-in
        assert appointment.status == (
            AppointmentStatusEnum.CONFIRMED
        )

        qr_code = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id,
            )
        )

        assert qr_code is not None
        assert qr_code.is_used is False

    finally:
        db.rollback()
        db.close()

def test_staff_check_in_invalid_token():
    db = SessionLocal()

    try:
        staff = db.scalar(
            select(User)
            .where(
                User.role
                == UserRoleEnum.HOSPITAL_STAFF,
            )
        )

        if staff is None:
            pytest.skip(
                "No hospital staff user found."
            )

        service = AppointmentQRCodeService(db)

        request = AppointmentQRCodeCheckInRequest(
            token="CF-INVALID-XX",
        )

        with pytest.raises(
            AppointmentQRCodeNotFoundException
        ):
            service.staff_check_in(
                request=request,
                current_user=staff,
            )

    finally:
        db.rollback()
        db.close()

def test_staff_check_in_with_used_qr():
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment)
            .join(
                AppointmentQRCode,
                AppointmentQRCode.appointment_id
                == Appointment.id,
            )
            .where(
                Appointment.status
                == AppointmentStatusEnum.CONFIRMED,
                AppointmentQRCode.is_used.is_(True),
            )
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        if appointment is None:
            pytest.skip(
                "No confirmed appointment with used QR code found."
            )

        staff = db.scalar(
            select(User)
            .where(
                User.role
                == UserRoleEnum.HOSPITAL_STAFF,
            )
        )

        if staff is None:
            pytest.skip(
                "No hospital staff user found."
            )

        qr_code = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id,
            )
        )

        if qr_code is None:
            pytest.skip(
                "QR code for appointment not found."
            )

        original_status = appointment.status

        service = AppointmentQRCodeService(db)

        request = AppointmentQRCodeCheckInRequest(
            token=qr_code.token,
        )

        with pytest.raises(
            AppointmentQRCodeAlreadyUsedException
        ):
            service.staff_check_in(
                request=request,
                current_user=staff,
            )

        db.refresh(appointment)
        db.refresh(qr_code)

        assert appointment.status == original_status
        assert qr_code.is_used is True
        assert qr_code.used_at is not None

    finally:
        db.rollback()
        db.close()

def test_staff_check_in_cancelled_appointment():
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment)
            .where(
                Appointment.status
                == AppointmentStatusEnum.CANCELLED,
            )
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        if appointment is None:
            pytest.skip(
                "No cancelled appointment found."
            )

        staff = db.scalar(
            select(User)
            .where(
                User.role
                == UserRoleEnum.HOSPITAL_STAFF,
            )
        )

        if staff is None:
            pytest.skip(
                "No hospital staff user found."
            )

        service = AppointmentQRCodeService(db)

        # สร้าง QR ไม่ได้สำหรับ CANCELLED
        # ดังนั้นใช้ QR ที่มีอยู่แล้วของ Appointment นี้
        qr_code = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id,
            )
        )

        if qr_code is None:
            pytest.skip(
                "No QR code found for cancelled appointment."
            )

        request = AppointmentQRCodeCheckInRequest(
            token=qr_code.token,
        )

        with pytest.raises(
            CannotCheckInCancelledAppointmentException
        ):
            service.staff_check_in(
                request=request,
                current_user=staff,
            )

        db.refresh(appointment)
        db.refresh(qr_code)

        assert appointment.status == (
            AppointmentStatusEnum.CANCELLED
        )

        assert qr_code.is_used is False

    finally:
        db.rollback()
        db.close()

@pytest.mark.parametrize(
    "appointment_status",
    [
        AppointmentStatusEnum.COMPLETED,
        AppointmentStatusEnum.NO_SHOW,
    ],
)
def test_staff_check_in_completed_or_no_show_appointment(
    appointment_status,
):
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment)
            .where(
                Appointment.status
                == appointment_status,
            )
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        if appointment is None:
            pytest.skip(
                f"No {appointment_status} appointment found."
            )

        staff = db.scalar(
            select(User)
            .where(
                User.role
                == UserRoleEnum.HOSPITAL_STAFF,
            )
        )

        if staff is None:
            pytest.skip(
                "No hospital staff user found."
            )

        qr_code = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id,
            )
        )

        if qr_code is None:
            pytest.skip(
                "No QR code found for appointment."
            )

        request = AppointmentQRCodeCheckInRequest(
            token=qr_code.token,
        )

        service = AppointmentQRCodeService(db)

        with pytest.raises(
            CannotGenerateAppointmentQRCodeException
        ):
            service.staff_check_in(
                request=request,
                current_user=staff,
            )

        db.refresh(appointment)
        db.refresh(qr_code)

        assert appointment.status == (
            appointment_status
        )

        assert qr_code.is_used is False

    finally:
        db.rollback()
        db.close()

def test_staff_check_in_too_early():
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment)
            .outerjoin(
                AppointmentQRCode,
                AppointmentQRCode.appointment_id
                == Appointment.id,
            )
            .where(
                Appointment.status
                == AppointmentStatusEnum.CONFIRMED,
                AppointmentQRCode.id.is_(None),
            )
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        if appointment is None:
            pytest.skip(
                "No confirmed appointment without QR code found."
            )

        staff = db.scalar(
            select(User)
            .where(
                User.role
                == UserRoleEnum.HOSPITAL_STAFF,
            )
        )

        if staff is None:
            pytest.skip(
                "No hospital staff user found."
            )

        now = datetime.now(
            ZoneInfo("Asia/Bangkok")
        ).replace(
            second=0,
            microsecond=0,
        )

        # กำหนด Appointment ให้อยู่ห่างจากปัจจุบัน
        # มากกว่า 1 ชั่วโมง จึงยังไม่ถึงช่วง Check-in
        appointment_start = now + timedelta(hours=2)

        for _ in range(120):
            conflict = db.scalar(
                select(Appointment)
                .where(
                    Appointment.doctor_id
                    == appointment.doctor_id,
                    Appointment.appointment_date
                    == appointment_start.date(),
                    Appointment.start_time
                    == appointment_start.time(),
                    Appointment.id != appointment.id,
                    Appointment.status.notin_(
                        [
                            AppointmentStatusEnum.CANCELLED,
                            AppointmentStatusEnum.COMPLETED,
                            AppointmentStatusEnum.NO_SHOW,
                        ]
                    ),
                )
            )

            if conflict is None:
                break

            appointment_start += timedelta(minutes=1)
        else:
            pytest.skip(
                "No available appointment time found."
            )

        appointment.appointment_date = (
            appointment_start.date()
        )

        appointment.start_time = (
            appointment_start.time()
        )

        appointment.end_time = (
            appointment_start
            + timedelta(minutes=30)
        ).time()

        db.flush()

        service = AppointmentQRCodeService(db)

        qr_result = service.get_qr(
            appointment.id
        )

        request = AppointmentQRCodeCheckInRequest(
            token=qr_result.token,
        )

        with pytest.raises(
            ConflictException
        ) as exc_info:
            service.staff_check_in(
                request=request,
                current_user=staff,
            )

        assert (
            "Check-in is available 1 hour before the appointment time."
            in str(exc_info.value.detail)
        )

        db.refresh(appointment)

        assert appointment.status == (
            AppointmentStatusEnum.CONFIRMED
        )

        qr_code = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id,
            )
        )

        assert qr_code is not None
        assert qr_code.is_used is False

    finally:
        db.rollback()
        db.close()