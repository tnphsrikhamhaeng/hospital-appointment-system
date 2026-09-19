import secrets

from datetime import (
    datetime,
    timedelta,
)
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.appointment_qr_repository import AppointmentQRCodeRepository

from app.models.appointment import Appointment
from app.models.appointment_qr_code import AppointmentQRCode
from app.models.user import User

from app.schemas.appointment_qr import (
    AppointmentQRCodeCheckInRequest,
    AppointmentQRCodeCheckInResponse,
    AppointmentQRCodeResponse,
    AppointmentQRCodeStaffCheckInPreviewResponse,
)

from app.core.enums import (
    AppointmentStatusEnum,
    UserRoleEnum,
)

from app.core.exceptions import (
    AppointmentNotFoundException,
    AppointmentQRCodeAlreadyUsedException,
    AppointmentQRCodeExpiredException,
    AppointmentQRCodeNotFoundException,
    CannotCheckInCancelledAppointmentException,
    CannotGenerateAppointmentQRCodeException,
    ConflictException,
    ForbiddenException,
)


BANGKOK_TZ = ZoneInfo("Asia/Bangkok")

QR_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class AppointmentQRCodeService:

    def __init__(self, db: Session):
        self.db = db

        self.appointment_repository = AppointmentRepository(db)

        self.qr_repository = AppointmentQRCodeRepository(db)

    def get_qr(
        self,
        appointment_id,
    ) -> AppointmentQRCodeResponse:

        appointment = self.appointment_repository.get_by_id(
            appointment_id
        )

        if appointment is None:
            raise AppointmentNotFoundException()

        if appointment.status in (
            AppointmentStatusEnum.CANCELLED,
            AppointmentStatusEnum.COMPLETED,
            AppointmentStatusEnum.NO_SHOW,
        ):
            raise CannotGenerateAppointmentQRCodeException()

        qr_code = self.qr_repository.get_by_appointment(
            appointment.id
        )

        if qr_code is None:
            qr_code = self._generate_qr(
                appointment
            )
        else:
            appointment_start = self._get_appointment_start(
                appointment
            )

            qr_code.expired_at = (
                appointment_start + timedelta(minutes=15)
            )

            self.qr_repository.update(qr_code)

            self.db.commit()

        return AppointmentQRCodeResponse.model_validate(
            qr_code
        )

    def _get_appointment_start(
        self,
        appointment: Appointment,
    ) -> datetime:

        return datetime.combine(
            appointment.appointment_date,
            appointment.start_time,
            tzinfo=BANGKOK_TZ,
        )

    def _generate_short_token(self) -> str:
        while True:
            random_part = "".join(
                secrets.choice(QR_CODE_ALPHABET)
                for _ in range(6)
            )

            token = f"CF-{random_part[:4]}-{random_part[4:]}"

            existing_qr = self.qr_repository.get_by_token(
                token
            )

            if existing_qr is None:
                return token

    def _generate_qr(
        self,
        appointment: Appointment,
    ) -> AppointmentQRCode:

        token = self._generate_short_token()

        appointment_start = self._get_appointment_start(
            appointment
        )

        expired_at = (
            appointment_start
            + timedelta(minutes=15)
        )

        qr_code = AppointmentQRCode(
            appointment_id=appointment.id,
            token=token,
            expired_at=expired_at,
            is_used=False,
        )

        qr_code = self.qr_repository.create(
            qr_code
        )

        self.db.commit()

        return qr_code

    def check_in(
        self,
        request: AppointmentQRCodeCheckInRequest,
        current_user: User,
    ) -> AppointmentQRCodeCheckInResponse:

        qr_code = self.qr_repository.get_by_token(
            request.token
        )

        if qr_code is None:
            raise AppointmentQRCodeNotFoundException()

        if qr_code.is_used:
            raise AppointmentQRCodeAlreadyUsedException()

        appointment = self.appointment_repository.get_by_id(
            qr_code.appointment_id
        )

        if appointment is None:
            raise AppointmentNotFoundException()

        if appointment.patient_id != current_user.id:
            raise ForbiddenException()

        if appointment.status == AppointmentStatusEnum.CANCELLED:
            raise CannotCheckInCancelledAppointmentException()

        if appointment.status in (
            AppointmentStatusEnum.COMPLETED,
            AppointmentStatusEnum.NO_SHOW,
        ):
            raise CannotGenerateAppointmentQRCodeException()

        now = datetime.now(BANGKOK_TZ)

        appointment_start = self._get_appointment_start(
            appointment
        )

        check_in_start = (
            appointment_start
            - timedelta(hours=1)
        )

        check_in_expired = (
            appointment_start
            + timedelta(minutes=15)
        )

        if now < check_in_start:
            raise ConflictException(
                detail=(
                    "Check-in is available "
                    "1 hour before the appointment time."
                )
            )

        if now >= check_in_expired:
            appointment.status = AppointmentStatusEnum.NO_SHOW

            self.appointment_repository.update(
                appointment
            )

            self.db.commit()

            raise AppointmentQRCodeExpiredException()

        qr_code.is_used = True
        qr_code.used_at = now

        appointment.status = AppointmentStatusEnum.CHECKED_IN

        self.qr_repository.update(
            qr_code
        )

        self.appointment_repository.update(
            appointment
        )

        self.db.commit()

        return AppointmentQRCodeCheckInResponse(
            message="Check-in successful."
        )

    def staff_check_in_preview(
        self,
        request: AppointmentQRCodeCheckInRequest,
        current_user: User,
    ) -> AppointmentQRCodeStaffCheckInPreviewResponse:

        if current_user.role != UserRoleEnum.HOSPITAL_STAFF:
            raise ForbiddenException()

        qr_code = self.qr_repository.get_by_token(
            request.token
        )

        if qr_code is None:
            raise AppointmentQRCodeNotFoundException()

        if qr_code.is_used:
            raise AppointmentQRCodeAlreadyUsedException()

        appointment = self.appointment_repository.get_by_id(
            qr_code.appointment_id
        )

        if appointment is None:
            raise AppointmentNotFoundException()

        if appointment.status == AppointmentStatusEnum.CANCELLED:
            raise CannotCheckInCancelledAppointmentException()

        if appointment.status in (
            AppointmentStatusEnum.COMPLETED,
            AppointmentStatusEnum.NO_SHOW,
        ):
            raise CannotGenerateAppointmentQRCodeException()

        if appointment.status != AppointmentStatusEnum.CONFIRMED:
            raise ConflictException(
                detail=(
                    "Only confirmed appointments "
                    "can be checked in by hospital staff."
                )
            )

        now = datetime.now(BANGKOK_TZ)

        appointment_start = self._get_appointment_start(
            appointment
        )

        check_in_start = (
            appointment_start
            - timedelta(hours=1)
        )

        check_in_expired = (
            appointment_start
            + timedelta(minutes=15)
        )

        if now < check_in_start:
            raise ConflictException(
                detail=(
                    "Check-in is available "
                    "1 hour before the appointment time."
                )
            )

        if now >= check_in_expired:
            raise AppointmentQRCodeExpiredException()

        patient_name = (
            f"{appointment.patient.first_name} "
            f"{appointment.patient.last_name}"
        )

        doctor_name = (
            f"{appointment.doctor.first_name} "
            f"{appointment.doctor.last_name}"
        )

        return AppointmentQRCodeStaffCheckInPreviewResponse(
            appointment_id=appointment.id,
            patient_name=patient_name,
            appointment_date=appointment.appointment_date,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            doctor_name=doctor_name,
            department_name=appointment.department.name,
        )

    def staff_check_in(
        self,
        request: AppointmentQRCodeCheckInRequest,
        current_user: User,
    ) -> AppointmentQRCodeCheckInResponse:

        if current_user.role != UserRoleEnum.HOSPITAL_STAFF:
            raise ForbiddenException()

        qr_code = self.qr_repository.get_by_token(
            request.token
        )

        if qr_code is None:
            raise AppointmentQRCodeNotFoundException()

        if qr_code.is_used:
            raise AppointmentQRCodeAlreadyUsedException()

        appointment = self.appointment_repository.get_by_id(
            qr_code.appointment_id
        )

        if appointment is None:
            raise AppointmentNotFoundException()

        if appointment.status == AppointmentStatusEnum.CANCELLED:
            raise CannotCheckInCancelledAppointmentException()

        if appointment.status in (
            AppointmentStatusEnum.COMPLETED,
            AppointmentStatusEnum.NO_SHOW,
        ):
            raise CannotGenerateAppointmentQRCodeException()

        if appointment.status != AppointmentStatusEnum.CONFIRMED:
            raise ConflictException(
                detail=(
                    "Only confirmed appointments "
                    "can be checked in by hospital staff."
                )
            )

        now = datetime.now(BANGKOK_TZ)

        appointment_start = self._get_appointment_start(
            appointment
        )

        check_in_start = (
            appointment_start
            - timedelta(hours=1)
        )

        check_in_expired = (
            appointment_start
            + timedelta(minutes=15)
        )

        if now < check_in_start:
            raise ConflictException(
                detail=(
                    "Check-in is available "
                    "1 hour before the appointment time."
                )
            )

        if now >= check_in_expired:
            appointment.status = AppointmentStatusEnum.NO_SHOW

            self.appointment_repository.update(
                appointment
            )

            self.db.commit()

            raise AppointmentQRCodeExpiredException()

        qr_code.is_used = True
        qr_code.used_at = now

        appointment.status = AppointmentStatusEnum.CHECKED_IN

        self.qr_repository.update(
            qr_code
        )

        self.appointment_repository.update(
            appointment
        )

        self.db.commit()

        return AppointmentQRCodeCheckInResponse(
            message="Check-in successful."
        )