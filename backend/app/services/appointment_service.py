from __future__ import annotations

import uuid

from datetime import datetime, timedelta, timezone, date, time
from zoneinfo import ZoneInfo

from fastapi import BackgroundTasks

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.enums import (
    AppointmentStatusEnum,
    DepartmentStatusEnum,
    DoctorStatusEnum,
    NotificationTypeEnum,
    UserRoleEnum,
    WeekdayEnum,
)
from app.core.exceptions import (
    ConflictException,
    NotFoundException,
)
from app.models.appointment import Appointment
from app.models.department import Department
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.department_repository import DepartmentRepository
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.doctor_schedule_template_repository import (
    DoctorScheduleTemplateRepository,
)
from app.repositories.user_repository import UserRepository
from app.schemas.appointment import (
    AppointmentCreateRequest,
    AppointmentResponse,
    AppointmentCancelRequest,
    AppointmentStatusUpdateRequest,
    AppointmentRescheduleRequest,
    DoctorScheduleResponse,
)
from app.services.notification_service import NotificationService


_FINAL_STATUSES = (
    AppointmentStatusEnum.CANCELLED,
    AppointmentStatusEnum.COMPLETED,
)

HOSPITAL_TIMEZONE = ZoneInfo("Asia/Bangkok")
NO_SHOW_WAIT_MINUTES = 15


class AppointmentService:

    _ALLOWED_TRANSITIONS = {
        AppointmentStatusEnum.CONFIRMED: {
            AppointmentStatusEnum.CHECKED_IN,
            AppointmentStatusEnum.CANCELLED,
            AppointmentStatusEnum.NO_SHOW,
        },
        AppointmentStatusEnum.CHECKED_IN: {
            AppointmentStatusEnum.IN_PROGRESS,
            AppointmentStatusEnum.COMPLETED,
            AppointmentStatusEnum.NO_SHOW,
        },
        AppointmentStatusEnum.IN_PROGRESS: {
            AppointmentStatusEnum.NO_SHOW,
        },
    }

    def __init__(self, db: Session):
        self.db = db

        self.appointment_repository = AppointmentRepository(db)
        self.user_repository = UserRepository(db)
        self.doctor_repository = DoctorRepository(db)
        self.department_repository = DepartmentRepository(db)
        self.schedule_repository = (
            DoctorScheduleTemplateRepository(db)
        )

    # =========================================================
    # CREATE APPOINTMENT
    # =========================================================

    def create_appointment(
        self,
        patient_id,
        request: AppointmentCreateRequest,
        background_tasks: BackgroundTasks,
    ) -> AppointmentResponse:

        patient = self.user_repository.get_by_id(patient_id)

        if patient is None:
            raise NotFoundException(
                detail="Patient not found."
            )

        doctor = self._get_active_doctor(
            request.doctor_id
        )

        department = self._get_active_department(
            doctor.department_id
        )

        self._ensure_not_in_past(
            request.appointment_date,
            request.start_time,
        )

        end_time = self._validate_slot(
            doctor_id=doctor.id,
            department=department,
            appointment_date=request.appointment_date,
            start_time=request.start_time,
        )

        self._ensure_no_overlap(
            doctor_id=doctor.id,
            appointment_date=request.appointment_date,
            start_time=request.start_time,
            end_time=end_time,
        )

        self._ensure_no_patient_overlap(
            patient_id=patient.id,
            appointment_date=request.appointment_date,
            start_time=request.start_time,
            end_time=end_time,
        )

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            department_id=department.id,
            appointment_date=request.appointment_date,
            start_time=request.start_time,
            end_time=end_time,
            reason=request.reason,
            status=AppointmentStatusEnum.CONFIRMED,
            confirmed_at=datetime.now(timezone.utc),
        )

        appointment = self.appointment_repository.create(
            appointment
        )

        # =====================================================
        # COMMIT APPOINTMENT FIRST
        # =====================================================

        self.db.commit()
        self.db.refresh(appointment)

        # =====================================================
        # SEND NOTIFICATION IN BACKGROUND
        # =====================================================

        background_tasks.add_task(
            self._send_appointment_notification_background,
            appointment.id,
            NotificationTypeEnum.APPOINTMENT_CONFIRMED,
            "ยืนยันการนัดหมาย",
            (
                "การนัดหมายของคุณได้รับการยืนยันแล้ว "
                f"{self._format_appointment_datetime(appointment)}"
            ),
        )

        return AppointmentResponse.model_validate(
            appointment
        )

    # =========================================================
    # GET APPOINTMENT
    # =========================================================

    def get_appointment(
        self,
        appointment_id,
    ) -> AppointmentResponse:

        appointment = self.appointment_repository.get_by_id(
            appointment_id
        )

        if appointment is None:
            raise NotFoundException(
                detail="Appointment not found."
            )

        return AppointmentResponse.model_validate(
            appointment
        )

    # =========================================================
    # GET APPOINTMENT PATIENT
    # =========================================================

    def get_appointment_patient(
        self,
        appointment_id,
        current_user,
    ):
        appointment = self._get_appointment_or_404(
            appointment_id
        )

        if current_user.role != UserRoleEnum.DOCTOR:
            raise ConflictException(
                detail=(
                    "Only doctor can view "
                    "appointment patient information."
                )
            )

        doctor = self.doctor_repository.get_by_user_id(
            current_user.id
        )

        if doctor is None:
            raise NotFoundException(
                detail="Doctor profile not found."
            )

        if appointment.doctor_id != doctor.id:
            raise ConflictException(
                detail=(
                    "Doctor can only view "
                    "their own appointment patients."
                )
            )

        patient = self.user_repository.get_by_id(
            appointment.patient_id
        )

        if patient is None:
            raise NotFoundException(
                detail="Patient not found."
            )

        return patient

    # =========================================================
    # GET PATIENT APPOINTMENTS
    # =========================================================

    def get_patient_appointments(
        self,
        patient_id,
    ) -> list[AppointmentResponse]:

        patient = self.user_repository.get_by_id(
            patient_id
        )

        if patient is None:
            raise NotFoundException(
                detail="Patient not found."
            )

        appointments = (
            self.appointment_repository.get_by_patient(
                patient_id
            )
        )

        return [
            AppointmentResponse.model_validate(
                appointment
            )
            for appointment in appointments
        ]

    # =========================================================
    # GET DOCTOR APPOINTMENTS
    # =========================================================

    def get_doctor_appointments(
        self,
        doctor_id,
    ) -> list[AppointmentResponse]:

        doctor = self.doctor_repository.get_by_id(
            doctor_id
        )

        if doctor is None:
            raise NotFoundException(
                detail="Doctor not found."
            )

        appointments = (
            self.appointment_repository.get_by_doctor(
                doctor_id
            )
        )

        return [
            AppointmentResponse.model_validate(
                appointment
            )
            for appointment in appointments
        ]

    # =========================================================
    # GET DOCTOR SCHEDULE
    # =========================================================

    def get_doctor_schedule(
        self,
        doctor_id,
        appointment_date,
    ) -> list[DoctorScheduleResponse]:

        doctor = self.doctor_repository.get_by_id(
            doctor_id
        )

        if doctor is None:
            raise NotFoundException(
                detail="Doctor not found."
            )

        appointments = (
            self.appointment_repository.get_by_doctor_date(
                doctor_id,
                appointment_date,
            )
        )

        return [
            DoctorScheduleResponse(
                id=appointment.id,
                patient_id=appointment.patient_id,
                patient_name=(
                    f"{appointment.patient.first_name} "
                    f"{appointment.patient.last_name}"
                ),
                appointment_date=appointment.appointment_date,
                start_time=appointment.start_time,
                end_time=appointment.end_time,
                status=appointment.status,
            )
            for appointment in appointments
        ]

    # =========================================================
    # CANCEL APPOINTMENT
    # =========================================================

    def cancel_appointment(
        self,
        appointment_id,
        request: AppointmentCancelRequest,
        background_tasks: BackgroundTasks,
    ) -> AppointmentResponse:

        appointment = self._get_appointment_or_404(
            appointment_id
        )

        self._transition_status(
            appointment,
            AppointmentStatusEnum.CANCELLED,
        )

        appointment.cancelled_reason = (
            request.cancelled_reason
        )

        appointment.cancelled_at = (
            datetime.now(timezone.utc)
        )

        self.appointment_repository.update(
            appointment
        )

        # =====================================================
        # COMMIT FIRST
        # =====================================================

        self.db.commit()
        self.db.refresh(appointment)

        # =====================================================
        # SEND NOTIFICATION IN BACKGROUND
        # =====================================================

        background_tasks.add_task(
            self._send_appointment_notification_background,
            appointment.id,
            NotificationTypeEnum.APPOINTMENT_CANCELLED,
            "ยกเลิกการนัดหมาย",
            (
                "การนัดหมายของคุณถูกยกเลิกแล้ว "
                f"{self._format_appointment_datetime(appointment)}"
            ),
        )

        return AppointmentResponse.model_validate(
            appointment
        )

    # =========================================================
    # UPDATE STATUS
    # =========================================================

    def update_status(
        self,
        appointment_id,
        request: AppointmentStatusUpdateRequest,
        current_user,
        background_tasks: BackgroundTasks,
    ) -> AppointmentResponse:

        appointment = self._get_appointment_or_404(
            appointment_id
        )

        # =====================================================
        # HOSPITAL STAFF
        # CONFIRMED -> CHECKED_IN only
        # =====================================================

        if current_user.role == UserRoleEnum.HOSPITAL_STAFF:

            if (
                request.status
                != AppointmentStatusEnum.CHECKED_IN
            ):
                raise ConflictException(
                    detail=(
                        "Hospital staff can only change "
                        "appointment status to CHECKED_IN."
                    )
                )

            if request.room_number is not None:
                raise ConflictException(
                    detail=(
                        "Room number is only required "
                        "when doctor calls a patient."
                    )
                )

        # =====================================================
        # DOCTOR
        # CHECKED_IN -> IN_PROGRESS
        # IN_PROGRESS -> NO_SHOW
        # =====================================================

        elif current_user.role == UserRoleEnum.DOCTOR:

            doctor = self.doctor_repository.get_by_user_id(
                current_user.id
            )

            if doctor is None:
                raise NotFoundException(
                    detail="Doctor profile not found."
                )

            if appointment.doctor_id != doctor.id:
                raise ConflictException(
                    detail=(
                        "Doctor can only update "
                        "their own appointments."
                    )
                )

            # -------------------------------------------------
            # Doctor calls patient
            # -------------------------------------------------

            if (
                request.status
                == AppointmentStatusEnum.IN_PROGRESS
            ):

                self._ensure_call_allowed(
                    appointment
                )

                if request.room_number is None:
                    raise ConflictException(
                        detail=(
                            "Room number is required "
                            "when doctor calls a patient."
                        )
                    )

            # -------------------------------------------------
            # Doctor marks patient as NO_SHOW
            # -------------------------------------------------

            elif (
                request.status
                == AppointmentStatusEnum.NO_SHOW
            ):

                if request.room_number is not None:
                    raise ConflictException(
                        detail=(
                            "Room number is not required "
                            "when marking patient as NO_SHOW."
                        )
                    )

                self._ensure_no_show_allowed(
                    appointment
                )

            else:
                raise ConflictException(
                    detail=(
                        "Doctor can only change "
                        "appointment status to "
                        "IN_PROGRESS or NO_SHOW."
                    )
                )

        else:
            raise ConflictException(
                detail=(
                    "Current user is not allowed "
                    "to update appointment status."
                )
            )

        # =====================================================
        # UPDATE STATUS
        # =====================================================

        self._transition_status(
            appointment,
            request.status,
        )

        self.appointment_repository.update(
            appointment
        )

        # =====================================================
        # COMMIT FIRST
        # =====================================================

        self.db.commit()
        self.db.refresh(appointment)

        # =====================================================
        # NOTIFICATION IN BACKGROUND
        # =====================================================

        if request.status == AppointmentStatusEnum.CHECKED_IN:

            background_tasks.add_task(
                self._send_status_notification_background,
                appointment.id,
                request.status,
                None,
            )

        elif request.status == AppointmentStatusEnum.IN_PROGRESS:

            background_tasks.add_task(
                self._send_status_notification_background,
                appointment.id,
                request.status,
                request.room_number,
            )

        elif request.status == AppointmentStatusEnum.NO_SHOW:

            background_tasks.add_task(
                self._send_status_notification_background,
                appointment.id,
                request.status,
                None,
            )

        return AppointmentResponse.model_validate(
            appointment
        )

    # =========================================================
    # RESCHEDULE APPOINTMENT
    # =========================================================

    def reschedule_appointment(
        self,
        appointment_id,
        request: AppointmentRescheduleRequest,
        background_tasks: BackgroundTasks,
    ) -> AppointmentResponse:

        appointment = self._get_appointment_or_404(
            appointment_id
        )

        if appointment.status in _FINAL_STATUSES:
            raise ConflictException(
                detail=(
                    f"Appointment with status "
                    f"'{appointment.status.value}' "
                    "cannot be rescheduled."
                )
            )

        doctor = self._get_active_doctor(
            appointment.doctor_id
        )

        department = self._get_active_department(
            appointment.department_id
        )

        self._ensure_not_in_past(
            request.appointment_date,
            request.start_time,
        )

        end_time = self._validate_slot(
            doctor_id=doctor.id,
            department=department,
            appointment_date=request.appointment_date,
            start_time=request.start_time,
        )

        self._ensure_no_overlap(
            doctor_id=appointment.doctor_id,
            appointment_date=request.appointment_date,
            start_time=request.start_time,
            end_time=end_time,
            exclude_appointment_id=appointment.id,
        )

        self._ensure_no_patient_overlap(
            patient_id=appointment.patient_id,
            appointment_date=request.appointment_date,
            start_time=request.start_time,
            end_time=end_time,
            exclude_appointment_id=appointment.id,
        )

        appointment.appointment_date = (
            request.appointment_date
        )

        appointment.start_time = request.start_time
        appointment.end_time = end_time
        appointment.status = (
            AppointmentStatusEnum.CONFIRMED
        )
        appointment.confirmed_at = (
            datetime.now(timezone.utc)
        )

        self.appointment_repository.update(
            appointment
        )

        # =====================================================
        # COMMIT FIRST
        # =====================================================

        self.db.commit()
        self.db.refresh(appointment)

        # =====================================================
        # SEND NOTIFICATION IN BACKGROUND
        # =====================================================

        background_tasks.add_task(
            self._send_appointment_notification_background,
            appointment.id,
            NotificationTypeEnum.APPOINTMENT_RESCHEDULED,
            "เลื่อนการนัดหมาย",
            (
                "การนัดหมายของคุณถูกเลื่อนแล้ว "
                f"{self._format_appointment_datetime(appointment)}"
            ),
        )

        return AppointmentResponse.model_validate(
            appointment
        )

    # =========================================================
    # SEARCH
    # =========================================================

    def search_appointments(
        self,
        *,
        patient_id=None,
        doctor_id=None,
        appointment_date=None,
        status=None,
    ) -> list[AppointmentResponse]:

        appointments = self.appointment_repository.search(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            status=status,
        )

        return [
            AppointmentResponse.model_validate(
                appointment
            )
            for appointment in appointments
        ]

    # =========================================================
    # HELPERS
    # =========================================================

    def _get_active_doctor(
        self,
        doctor_id,
    ):

        doctor = self.doctor_repository.get_by_id(
            doctor_id
        )

        if doctor is None:
            raise NotFoundException(
                detail="Doctor not found."
            )

        if doctor.status != DoctorStatusEnum.ACTIVE:
            raise ConflictException(
                detail="Doctor is inactive."
            )

        return doctor

    def _get_active_department(
        self,
        department_id,
    ):

        department = self.department_repository.get_by_id(
            department_id
        )

        if department is None:
            raise NotFoundException(
                detail="Department not found."
            )

        if department.status != DepartmentStatusEnum.ACTIVE:
            raise ConflictException(
                detail="Department is inactive."
            )

        return department

    def _get_appointment_or_404(
        self,
        appointment_id,
    ):

        appointment = (
            self.appointment_repository.get_by_id(
                appointment_id
            )
        )

        if appointment is None:
            raise NotFoundException(
                detail="Appointment not found."
            )

        return appointment

    def _ensure_not_in_past(
        self,
        appointment_date,
        start_time,
    ) -> None:

        appointment_datetime = datetime.combine(
            appointment_date,
            start_time,
        ).replace(
            tzinfo=HOSPITAL_TIMEZONE
        )

        minimum_booking_datetime = (
            datetime.now(HOSPITAL_TIMEZONE)
            + timedelta(hours=1)
        )

        if appointment_datetime < minimum_booking_datetime:
            raise ConflictException(
                detail=(
                    "Appointment must be booked "
                    "at least 1 hour in advance."
                )
            )

    def _ensure_call_allowed(
        self,
        appointment: Appointment,
    ) -> None:

        appointment_start = datetime.combine(
            appointment.appointment_date,
            appointment.start_time,
        ).replace(
            tzinfo=HOSPITAL_TIMEZONE
        )

        now = datetime.now(
            HOSPITAL_TIMEZONE
        )

        if now < appointment_start:
            raise ConflictException(
                detail=(
                    "Patient cannot be called "
                    "before the appointment time."
                )
            )

    def _ensure_no_show_allowed(
        self,
        appointment: Appointment,
    ) -> None:

        if (
            appointment.status
            != AppointmentStatusEnum.IN_PROGRESS
        ):
            raise ConflictException(
                detail=(
                    "Patient can only be marked "
                    "as NO_SHOW after the doctor "
                    "has called the patient."
                )
            )

        appointment_start = datetime.combine(
            appointment.appointment_date,
            appointment.start_time,
        ).replace(
            tzinfo=HOSPITAL_TIMEZONE
        )

        no_show_time = (
            appointment_start
            + timedelta(
                minutes=NO_SHOW_WAIT_MINUTES
            )
        )

        now = datetime.now(
            HOSPITAL_TIMEZONE
        )

        if now < no_show_time:

            remaining_seconds = (
                no_show_time - now
            ).total_seconds()

            remaining_minutes = max(
                1,
                int(
                    (remaining_seconds + 59)
                    // 60
                ),
            )

            raise ConflictException(
                detail=(
                    "Patient cannot be marked "
                    f"as NO_SHOW yet. "
                    f"Please wait {remaining_minutes} "
                    "more minute(s)."
                )
            )

    def _validate_slot(
        self,
        *,
        doctor_id: uuid.UUID,
        department: Department,
        appointment_date: date,
        start_time: time,
    ) -> time:

        weekday = WeekdayEnum(
            appointment_date.strftime("%A").lower()
        )

        schedule = self.schedule_repository.get_active_schedule(
            doctor_id=doctor_id,
            weekday=weekday,
            start_time=start_time,
        )

        if schedule is None:
            raise ConflictException(
                detail="Doctor is not available at this time."
            )

        appointment_start = datetime.combine(
            appointment_date,
            start_time,
        )

        appointment_end = (
            appointment_start
            + timedelta(
                minutes=department.slot_duration_minutes
            )
        )

        # ตารางปกติ
        if schedule.start_time <= schedule.end_time:

            schedule_start = datetime.combine(
                appointment_date,
                schedule.start_time,
            )

            schedule_end = datetime.combine(
                appointment_date,
                schedule.end_time,
            )

        # ตารางข้ามวัน เช่น 23:00 - 01:00
        else:

            if start_time >= schedule.start_time:

                schedule_start = datetime.combine(
                    appointment_date,
                    schedule.start_time,
                )

                schedule_end = datetime.combine(
                    appointment_date + timedelta(days=1),
                    schedule.end_time,
                )

            else:

                schedule_start = datetime.combine(
                    appointment_date - timedelta(days=1),
                    schedule.start_time,
                )

                schedule_end = datetime.combine(
                    appointment_date,
                    schedule.end_time,
                )

        if (
            appointment_start < schedule_start
            or appointment_end > schedule_end
        ):
            raise ConflictException(
                detail=(
                    "Appointment time is "
                    "outside doctor's schedule."
                )
            )

        return appointment_end.time()

    def _ensure_no_overlap(
        self,
        *,
        doctor_id,
        appointment_date,
        start_time,
        end_time,
        exclude_appointment_id=None,
    ):

        exists = (
            self.appointment_repository
            .exists_overlapping_appointment(
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                start_time=start_time,
                end_time=end_time,
                exclude_appointment_id=(
                    exclude_appointment_id
                ),
            )
        )

        if exists:
            raise ConflictException(
                detail=(
                    "Appointment slot is "
                    "already booked."
                )
            )

    def _ensure_no_patient_overlap(
        self,
        *,
        patient_id,
        appointment_date,
        start_time,
        end_time,
        exclude_appointment_id=None,
    ) -> None:

        exists = (
            self.appointment_repository
            .exists_overlapping_patient_appointment(
                patient_id=patient_id,
                appointment_date=appointment_date,
                start_time=start_time,
                end_time=end_time,
                exclude_appointment_id=(
                    exclude_appointment_id
                ),
            )
        )

        if exists:
            raise ConflictException(
                detail=(
                    "Patient already has "
                    "an appointment during "
                    "this time."
                )
            )

    def _transition_status(
        self,
        appointment: Appointment,
        new_status: AppointmentStatusEnum,
    ) -> None:

        if appointment.status in _FINAL_STATUSES:
            raise ConflictException(
                detail=(
                    f"Appointment with status "
                    f"'{appointment.status.value}' "
                    "cannot be changed."
                )
            )

        allowed_statuses = (
            self._ALLOWED_TRANSITIONS.get(
                appointment.status,
                set(),
            )
        )

        if new_status not in allowed_statuses:
            raise ConflictException(
                detail=(
                    f"Cannot change appointment status "
                    f"from '{appointment.status.value}' "
                    f"to '{new_status.value}'."
                )
            )

        appointment.status = new_status

    def _format_appointment_datetime(
        self,
        appointment: Appointment,
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

        day = appointment.appointment_date.day

        month = thai_months[
            appointment.appointment_date.month - 1
        ]

        year = (
            appointment.appointment_date.year
            + 543
        )

        appointment_time = appointment.start_time.strftime(
            "%H:%M"
        )

        return (
            f"วันที่ {day} {month} {year} "
            f"เวลา {appointment_time} น."
        )

    # =========================================================
    # BACKGROUND NOTIFICATION
    # =========================================================

    def _send_appointment_notification_background(
        self,
        appointment_id: uuid.UUID,
        notification_type: NotificationTypeEnum,
        title: str,
        body: str,
    ) -> None:

        db = SessionLocal()

        try:
            appointment_repository = (
                AppointmentRepository(db)
            )

            appointment = (
                appointment_repository.get_by_id(
                    appointment_id
                )
            )

            if appointment is None:
                return

            notification_service = (
                NotificationService(db)
            )

            notification_service.create_notification(
                appointment_id=appointment.id,
                patient_id=appointment.patient_id,
                notification_type=notification_type,
                title=title,
                body=body,
            )

            db.commit()

        except Exception :
            db.rollback()
            

        finally:
            db.close()

    # =========================================================
    # BACKGROUND STATUS NOTIFICATION
    # =========================================================

    def _send_status_notification_background(
        self,
        appointment_id: uuid.UUID,
        status: AppointmentStatusEnum,
        room_number: str | None = None,
    ) -> None:

        db = SessionLocal()

        try:
            appointment_repository = (
                AppointmentRepository(db)
            )

            notification_service = (
                NotificationService(db)
            )

            appointment = (
                appointment_repository.get_by_id(
                    appointment_id
                )
            )

            if appointment is None:
                return

            # -------------------------------------------------
            # CHECKED IN
            # -------------------------------------------------

            if status == AppointmentStatusEnum.CHECKED_IN:

                notification_service.create_notification(
                    appointment_id=appointment.id,
                    patient_id=appointment.patient_id,
                    notification_type=(
                        NotificationTypeEnum
                        .APPOINTMENT_CHECKED_IN
                    ),
                    title="เช็คอินสำเร็จ",
                    body=(
                        "คุณเช็คอินสำหรับการนัดหมายเรียบร้อยแล้ว "
                        "กรุณารอเรียกเข้าพบแพทย์"
                    ),
                )

            # -------------------------------------------------
            # IN PROGRESS
            # -------------------------------------------------

            elif status == AppointmentStatusEnum.IN_PROGRESS:

                notification_service.create_notification(
                    appointment_id=appointment.id,
                    patient_id=appointment.patient_id,
                    notification_type=(
                        NotificationTypeEnum
                        .READY_FOR_CONSULTATION
                    ),
                    title="พร้อมเข้ารับการตรวจ",
                    body=(
                        "แพทย์พร้อมให้บริการตรวจแล้ว "
                        f"กรุณาไปที่ห้องตรวจ {room_number} "
                        f"{self._format_appointment_datetime(appointment)}"
                    ),
                )

            # -------------------------------------------------
            # NO SHOW
            # -------------------------------------------------

            elif status == AppointmentStatusEnum.NO_SHOW:

                notification_service.create_notification(
                    appointment_id=appointment.id,
                    patient_id=appointment.patient_id,
                    notification_type=(
                        NotificationTypeEnum
                        .APPOINTMENT_CANCELLED
                    ),
                    title="ไม่มาตามนัด",
                    body=(
                        "ระบบบันทึกว่าคุณไม่มาตามนัดหมาย "
                        f"{self._format_appointment_datetime(appointment)}"
                    ),
                )

            db.commit()

        except Exception:
            db.rollback()

        finally:
            db.close()