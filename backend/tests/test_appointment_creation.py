from datetime import date, datetime, time, timedelta

import pytest
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.enums import (
    AppointmentStatusEnum,
    DepartmentStatusEnum,
    DoctorStatusEnum,
    UserRoleEnum,
    WeekdayEnum,
    NotificationStatusEnum
)
from app.core.exceptions import ConflictException
from app.models.appointment import Appointment
from app.models.department import Department
from app.models.doctor import Doctor
from app.models.doctor_schedule_template import DoctorScheduleTemplate
from app.models.user import User
from app.schemas.appointment import AppointmentCreateRequest
from app.services.appointment_service import AppointmentService
from app.schemas.appointment import AppointmentRescheduleRequest, AppointmentCancelRequest
from app.schemas.notification import NotificationTypeEnum
from app.models.notification_log import NotificationLog

def get_patient(db):
    patient = db.scalar(
        select(User)
        .where(User.role == UserRoleEnum.PATIENT)
        .limit(1)
    )

    if patient is None:
        pytest.skip("No patient found.")

    return patient


def get_active_doctor_with_schedule(db):
    rows = db.execute(
        select(
            Doctor,
            Department,
            DoctorScheduleTemplate,
        )
        .join(
            Department,
            Doctor.department_id == Department.id,
        )
        .join(
            DoctorScheduleTemplate,
            Doctor.id == DoctorScheduleTemplate.doctor_id,
        )
        .where(
            Doctor.status == DoctorStatusEnum.ACTIVE,
            Department.status == DepartmentStatusEnum.ACTIVE,
            DoctorScheduleTemplate.is_active.is_(True),
        )
        .order_by(
            DoctorScheduleTemplate.start_time,
        )
    ).first()

    if rows is None:
        pytest.skip(
            "No active doctor, department, and schedule found."
        )

    return rows


def get_future_schedule_date(schedule):
    weekday_map = {
        WeekdayEnum.MONDAY: 0,
        WeekdayEnum.TUESDAY: 1,
        WeekdayEnum.WEDNESDAY: 2,
        WeekdayEnum.THURSDAY: 3,
        WeekdayEnum.FRIDAY: 4,
        WeekdayEnum.SATURDAY: 5,
        WeekdayEnum.SUNDAY: 6,
    }

    today = date.today()
    target_weekday = weekday_map[schedule.weekday]

    days_ahead = (
        target_weekday - today.weekday()
    ) % 7

    if days_ahead == 0:
        days_ahead = 7

    return today + timedelta(days=days_ahead)


def build_valid_slot(
    doctor,
    department,
    schedule,
):
    appointment_date = get_future_schedule_date(
        schedule
    )

    slot_start = schedule.start_time

    slot_datetime = datetime.combine(
        appointment_date,
        slot_start,
    )

    minimum_datetime = (
        datetime.now()
        + timedelta(hours=1)
    )

    if slot_datetime < minimum_datetime:
        pytest.skip(
            "Selected schedule does not provide "
            "a slot at least 1 hour in advance."
        )

    slot_end_datetime = (
        slot_datetime
        + timedelta(
            minutes=department.slot_duration_minutes
        )
    )

    if slot_end_datetime.time() > schedule.end_time:
        pytest.skip(
            "Department slot duration exceeds schedule."
        )

    return appointment_date, slot_start


def test_create_appointment_success():
    db = SessionLocal()

    try:
        patient = get_patient(db)

        doctor, department, schedule = (
            get_active_doctor_with_schedule(db)
        )

        # หา slot ที่ยังไม่ถูกจอง
        appointment_date = date.today() + timedelta(days=1)

        start_time = schedule.start_time
        slot_duration = department.slot_duration_minutes

        while start_time < schedule.end_time:
            end_datetime = (
                datetime.combine(
                    appointment_date,
                    start_time,
                )
                + timedelta(minutes=slot_duration)
            )

            if end_datetime.time() > schedule.end_time:
                break

            exists = db.scalar(
                select(Appointment.id)
                .where(
                    Appointment.doctor_id == doctor.id,
                    Appointment.appointment_date
                    == appointment_date,
                    Appointment.status
                    != AppointmentStatusEnum.CANCELLED,
                    Appointment.start_time
                    < end_datetime.time(),
                    Appointment.end_time
                    > start_time,
                )
            )

            if exists is None:
                break

            start_time = (
                datetime.combine(
                    appointment_date,
                    start_time,
                )
                + timedelta(minutes=slot_duration)
            ).time()

        else:
            pytest.skip(
                "No available appointment slot found."
            )

        service = AppointmentService(db)

        request = AppointmentCreateRequest(
            doctor_id=doctor.id,
            appointment_date=appointment_date,
            start_time=start_time,
            reason="Automated QA",
        )

        result = service.create_appointment(
            patient_id=patient.id,
            request=request,
        )

        assert result is not None
        assert result.doctor_id == doctor.id
        assert result.appointment_date == appointment_date
        assert result.start_time == start_time

    finally:
        db.rollback()
        db.close()

def test_create_appointment_outside_schedule():
    db = SessionLocal()

    try:
        patient = get_patient(db)

        doctor, department, schedule = (
            get_active_doctor_with_schedule(db)
        )

        appointment_date = get_future_schedule_date(
            schedule
        )

        invalid_start = (
            datetime.combine(
                appointment_date,
                schedule.end_time,
            )
            + timedelta(minutes=1)
        ).time()

        service = AppointmentService(db)

        request = AppointmentCreateRequest(
            doctor_id=doctor.id,
            appointment_date=appointment_date,
            start_time=invalid_start,
        )

        with pytest.raises(ConflictException):
            service.create_appointment(
                patient_id=patient.id,
                request=request,
            )

        db.rollback()

    finally:
        db.close()


def test_create_appointment_too_soon():
    db = SessionLocal()

    try:
        patient = get_patient(db)

        doctor, department, schedule = (
            get_active_doctor_with_schedule(db)
        )

        now = datetime.now()

        appointment_date = date.today()

        start_time = (
            now + timedelta(minutes=30)
        ).time().replace(second=0, microsecond=0)

        request = AppointmentCreateRequest(
            doctor_id=doctor.id,
            appointment_date=appointment_date,
            start_time=start_time,
        )

        service = AppointmentService(db)

        with pytest.raises(ConflictException):
            service.create_appointment(
                patient_id=patient.id,
                request=request,
            )

        db.rollback()

    finally:
        db.close()


def test_create_appointment_inactive_doctor():
    db = SessionLocal()

    try:
        patient = get_patient(db)

        row = db.execute(
            select(
                Doctor,
                Department,
                DoctorScheduleTemplate,
            )
            .join(
                Department,
                Doctor.department_id == Department.id,
            )
            .join(
                DoctorScheduleTemplate,
                Doctor.id
                == DoctorScheduleTemplate.doctor_id,
            )
            .where(
                Doctor.status != DoctorStatusEnum.ACTIVE,
                Department.status
                == DepartmentStatusEnum.ACTIVE,
                DoctorScheduleTemplate.is_active.is_(True),
            )
            .limit(1)
        ).first()

        if row is None:
            pytest.skip("No inactive doctor with active schedule.")

        doctor, department, schedule = row

        appointment_date = get_future_schedule_date(
            schedule
        )

        request = AppointmentCreateRequest(
            doctor_id=doctor.id,
            appointment_date=appointment_date,
            start_time=schedule.start_time,
        )

        service = AppointmentService(db)

        with pytest.raises(ConflictException):
            service.create_appointment(
                patient_id=patient.id,
                request=request,
            )

    finally:
        db.rollback()
        db.close()


def test_create_appointment_inactive_department():
    db = SessionLocal()

    try:
        patient = get_patient(db)

        row = db.execute(
            select(
                Doctor,
                Department,
                DoctorScheduleTemplate,
            )
            .join(
                Department,
                Doctor.department_id == Department.id,
            )
            .join(
                DoctorScheduleTemplate,
                Doctor.id
                == DoctorScheduleTemplate.doctor_id,
            )
            .where(
                Doctor.status == DoctorStatusEnum.ACTIVE,
                Department.status
                != DepartmentStatusEnum.ACTIVE,
                DoctorScheduleTemplate.is_active.is_(True),
            )
            .limit(1)
        ).first()

        if row is None:
            pytest.skip(
                "No active doctor with inactive department."
            )

        doctor, department, schedule = row

        appointment_date = get_future_schedule_date(
            schedule
        )

        request = AppointmentCreateRequest(
            doctor_id=doctor.id,
            appointment_date=appointment_date,
            start_time=schedule.start_time,
        )

        service = AppointmentService(db)

        with pytest.raises(ConflictException):
            service.create_appointment(
                patient_id=patient.id,
                request=request,
            )

    finally:
        db.rollback()
        db.close()


def test_create_appointment_doctor_overlap():
    db = SessionLocal()

    try:
        patient = get_patient(db)

        now = datetime.now()

        appointment = db.scalar(
            select(Appointment)
            .where(
                Appointment.status
                != AppointmentStatusEnum.CANCELLED,
                Appointment.appointment_date > date.today(),
            )
            .order_by(
                Appointment.appointment_date.asc(),
                Appointment.start_time.asc(),
            )
        )

        if appointment is None:
            pytest.skip(
                "No future active appointment found."
            )

        appointment_datetime = datetime.combine(
            appointment.appointment_date,
            appointment.start_time,
        )

        if appointment_datetime < (
            now + timedelta(hours=1)
        ):
            pytest.skip(
                "No future appointment available "
                "at least 1 hour in advance."
            )

        doctor = db.scalar(
            select(Doctor).where(
                Doctor.id == appointment.doctor_id,
                Doctor.status == DoctorStatusEnum.ACTIVE,
            )
        )

        if doctor is None:
            pytest.skip(
                "No active doctor for existing appointment."
            )

        service = AppointmentService(db)

        request = AppointmentCreateRequest(
            doctor_id=appointment.doctor_id,
            appointment_date=appointment.appointment_date,
            start_time=appointment.start_time,
        )

        with pytest.raises(ConflictException):
            service.create_appointment(
                patient_id=patient.id,
                request=request,
            )

    finally:
        db.rollback()
        db.close()


def test_create_appointment_patient_overlap():
    db = SessionLocal()

    try:
        patient_appointment = db.scalar(
            select(Appointment)
            .where(
                Appointment.status
                != AppointmentStatusEnum.CANCELLED,
                Appointment.appointment_date > date.today(),
            )
            .order_by(
                Appointment.appointment_date.asc(),
                Appointment.start_time.asc(),
            )
        )

        if patient_appointment is None:
            pytest.skip(
                "No future active appointment found."
            )

        appointment_datetime = datetime.combine(
            patient_appointment.appointment_date,
            patient_appointment.start_time,
        )

        if appointment_datetime < (
            datetime.now() + timedelta(hours=1)
        ):
            pytest.skip(
                "No future appointment available "
                "at least 1 hour in advance."
            )

        patient = db.get(
            User,
            patient_appointment.patient_id,
        )

        if patient is None:
            pytest.skip(
                "Patient for existing appointment not found."
            )

        doctor = db.scalar(
            select(Doctor)
            .where(
                Doctor.status == DoctorStatusEnum.ACTIVE,
                Doctor.id
                != patient_appointment.doctor_id,
            )
            .limit(1)
        )

        if doctor is None:
            pytest.skip(
                "No second active doctor found."
            )

        service = AppointmentService(db)

        request = AppointmentCreateRequest(
            doctor_id=doctor.id,
            appointment_date=(
                patient_appointment.appointment_date
            ),
            start_time=patient_appointment.start_time,
        )

        with pytest.raises(ConflictException):
            service.create_appointment(
                patient_id=patient.id,
                request=request,
            )

    finally:
        db.rollback()
        db.close()
        
def test_reschedule_appointment_success():
    db = SessionLocal()

    try:
        patient = get_patient(db)

        doctor, department, schedule = (
            get_active_doctor_with_schedule(db)
        )

        original_date = date.today() + timedelta(days=2)

        slot_duration = department.slot_duration_minutes

        start_time = schedule.start_time

        end_datetime = (
            datetime.combine(
                original_date,
                start_time,
            )
            + timedelta(minutes=slot_duration)
        )

        if end_datetime.time() > schedule.end_time:
            pytest.skip(
                "No valid appointment slot found."
            )

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            department_id=department.id,
            appointment_date=original_date,
            start_time=start_time,
            end_time=end_datetime.time(),
            status=AppointmentStatusEnum.CONFIRMED,
            reason="Reschedule QA",
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        new_date = original_date + timedelta(days=1)

        new_start_time = schedule.start_time

        new_end_datetime = (
            datetime.combine(
                new_date,
                new_start_time,
            )
            + timedelta(minutes=slot_duration)
        )

        if new_end_datetime.time() > schedule.end_time:
            pytest.skip(
                "No valid reschedule slot found."
            )

        request = AppointmentRescheduleRequest(
            appointment_date=new_date,
            start_time=new_start_time,
        )

        service = AppointmentService(db)

        result = service.reschedule_appointment(
            appointment_id=appointment.id,
            request=request,
        )

        assert result.id == appointment.id
        assert result.appointment_date == new_date
        assert result.start_time == new_start_time
        assert result.end_time == new_end_datetime.time()
        assert result.status == AppointmentStatusEnum.CONFIRMED

    finally:
        db.rollback()
        db.close()
        
def test_reschedule_appointment_doctor_overlap():
    db = SessionLocal()

    try:
        existing = db.scalar(
            select(Appointment)
            .where(
                Appointment.status
                != AppointmentStatusEnum.CANCELLED,
                Appointment.appointment_date > date.today(),
            )
            .order_by(
                Appointment.appointment_date.asc(),
                Appointment.start_time.asc(),
            )
        )

        if existing is None:
            pytest.skip(
                "No future active appointment found."
            )

        doctor = db.get(
            Doctor,
            existing.doctor_id,
        )

        department = db.get(
            Department,
            existing.department_id,
        )

        if doctor is None or department is None:
            pytest.skip(
                "Doctor or department not found."
            )

        patient = db.scalar(
            select(User)
            .where(
                User.role == UserRoleEnum.PATIENT,
                User.id != existing.patient_id,
            )
        )

        if patient is None:
            pytest.skip(
                "No second patient found."
            )

        appointment_start = (
          datetime.combine(
              existing.appointment_date,
              existing.start_time,
          )
          - timedelta(
              minutes=department.slot_duration_minutes
          )
      ).time()

        appointment_end = existing.start_time

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            department_id=department.id,
            appointment_date=existing.appointment_date,
            start_time=appointment_start,
            end_time=appointment_end,
            status=AppointmentStatusEnum.CONFIRMED,
            reason="Reschedule Doctor Overlap QA",
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        original_date = appointment.appointment_date
        original_time = appointment.start_time

        request = AppointmentRescheduleRequest(
            appointment_date=existing.appointment_date,
            start_time=existing.start_time,
        )

        service = AppointmentService(db)

        with pytest.raises(ConflictException):
            service.reschedule_appointment(
                appointment_id=appointment.id,
                request=request,
            )

        db.refresh(appointment)

        assert appointment.appointment_date == original_date
        assert appointment.start_time == original_time

    finally:
        db.rollback()
        db.close()
        
def test_reschedule_appointment_patient_overlap():
    db = SessionLocal()

    try:
        existing = db.scalar(
            select(Appointment)
            .where(
                Appointment.status
                != AppointmentStatusEnum.CANCELLED,
                Appointment.appointment_date > date.today(),
            )
            .order_by(
                Appointment.appointment_date.asc(),
                Appointment.start_time.asc(),
            )
        )

        if existing is None:
            pytest.skip(
                "No future active appointment found."
            )

        patient = db.get(
            User,
            existing.patient_id,
        )

        if patient is None:
            pytest.skip(
                "Patient not found."
            )

        doctor = db.scalar(
            select(Doctor)
            .where(
                Doctor.status == DoctorStatusEnum.ACTIVE,
                Doctor.id != existing.doctor_id,
            )
        )

        if doctor is None:
            pytest.skip(
                "No second active doctor found."
            )

        department = db.get(
            Department,
            doctor.department_id,
        )

        if department is None:
            pytest.skip(
                "Department not found."
            )

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            department_id=department.id,
            appointment_date=(
                existing.appointment_date
            ),
            start_time=existing.start_time,
            end_time=(
                datetime.combine(
                    existing.appointment_date,
                    existing.start_time,
                )
                + timedelta(
                    minutes=department.slot_duration_minutes
                )
            ).time(),
            status=AppointmentStatusEnum.CONFIRMED,
            reason="Reschedule Patient Overlap QA",
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        original_date = appointment.appointment_date
        original_time = appointment.start_time

        request = AppointmentRescheduleRequest(
            appointment_date=existing.appointment_date,
            start_time=existing.start_time,
        )

        service = AppointmentService(db)

        with pytest.raises(ConflictException):
            service.reschedule_appointment(
                appointment_id=appointment.id,
                request=request,
            )

        db.refresh(appointment)

        assert appointment.appointment_date == original_date
        assert appointment.start_time == original_time

    finally:
        db.rollback()
        db.close()
        

def test_reschedule_appointment_too_soon():
    db = SessionLocal()

    try:
        patient = get_patient(db)

        doctor, department, schedule = (
            get_active_doctor_with_schedule(db)
        )

        appointment_date = date.today() + timedelta(days=2)

        slot_duration = department.slot_duration_minutes
        start_time = schedule.start_time

        while start_time < schedule.end_time:
            end_datetime = (
                datetime.combine(
                    appointment_date,
                    start_time,
                )
                + timedelta(minutes=slot_duration)
            )

            if end_datetime.time() > schedule.end_time:
                break

            exists = db.scalar(
                select(Appointment.id)
                .where(
                    Appointment.doctor_id == doctor.id,
                    Appointment.appointment_date
                    == appointment_date,
                    Appointment.status
                    != AppointmentStatusEnum.CANCELLED,
                    Appointment.start_time
                    < end_datetime.time(),
                    Appointment.end_time
                    > start_time,
                )
            )

            if exists is None:
                break

            start_time = (
                datetime.combine(
                    appointment_date,
                    start_time,
                )
                + timedelta(minutes=slot_duration)
            ).time()
        else:
            pytest.skip(
                "No available appointment slot found."
            )

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            department_id=department.id,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_datetime.time(),
            status=AppointmentStatusEnum.CONFIRMED,
            reason="Reschedule Too Soon QA",
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        # ใช้เวลาที่อยู่ในอนาคต แต่ไม่ถึง 1 ชั่วโมง
        too_soon = datetime.now() + timedelta(
            minutes=30
        )

        request = AppointmentRescheduleRequest(
            appointment_date=too_soon.date(),
            start_time=too_soon.time().replace(
                second=0,
                microsecond=0,
            ),
        )

        service = AppointmentService(db)

        with pytest.raises(ConflictException):
            service.reschedule_appointment(
                appointment_id=appointment.id,
                request=request,
            )

    finally:
        db.rollback()
        db.close()
        
def test_reschedule_appointment_outside_schedule():
    db = SessionLocal()

    try:
        patient = get_patient(db)

        doctor, department, schedule = (
            get_active_doctor_with_schedule(db)
        )

        appointment_date = date.today() + timedelta(days=2)

        slot_duration = department.slot_duration_minutes
        start_time = schedule.start_time

        while start_time < schedule.end_time:
            end_datetime = (
                datetime.combine(
                    appointment_date,
                    start_time,
                )
                + timedelta(minutes=slot_duration)
            )

            if end_datetime.time() > schedule.end_time:
                break

            exists = db.scalar(
                select(Appointment.id)
                .where(
                    Appointment.doctor_id == doctor.id,
                    Appointment.appointment_date
                    == appointment_date,
                    Appointment.status
                    != AppointmentStatusEnum.CANCELLED,
                    Appointment.start_time
                    < end_datetime.time(),
                    Appointment.end_time
                    > start_time,
                )
            )

            if exists is None:
                break

            start_time = (
                datetime.combine(
                    appointment_date,
                    start_time,
                )
                + timedelta(minutes=slot_duration)
            ).time()
        else:
            pytest.skip(
                "No available appointment slot found."
            )

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            department_id=department.id,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_datetime.time(),
            status=AppointmentStatusEnum.CONFIRMED,
            reason="Reschedule Outside Schedule QA",
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        original_date = appointment.appointment_date
        original_time = appointment.start_time

        # เลื่อนไปเวลาที่อยู่นอก Schedule
        outside_start = schedule.end_time

        request = AppointmentRescheduleRequest(
            appointment_date=appointment_date,
            start_time=outside_start,
        )

        service = AppointmentService(db)

        with pytest.raises(ConflictException):
            service.reschedule_appointment(
                appointment_id=appointment.id,
                request=request,
            )

        db.refresh(appointment)

        assert appointment.appointment_date == original_date
        assert appointment.start_time == original_time

    finally:
        db.rollback()
        db.close()

def test_reschedule_appointment_final_status():
    db = SessionLocal()

    try:
        patient = get_patient(db)

        doctor, department, schedule = (
            get_active_doctor_with_schedule(db)
        )

        appointment_date = date.today() + timedelta(days=2)

        slot_duration = department.slot_duration_minutes
        start_time = schedule.start_time

        end_datetime = (
            datetime.combine(
                appointment_date,
                start_time,
            )
            + timedelta(minutes=slot_duration)
        )

        if end_datetime.time() > schedule.end_time:
            pytest.skip(
                "No valid appointment slot found."
            )

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            department_id=department.id,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_datetime.time(),
            status=AppointmentStatusEnum.CANCELLED,
            reason="Reschedule Final Status QA",
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        original_date = appointment.appointment_date
        original_time = appointment.start_time
        original_status = appointment.status

        request = AppointmentRescheduleRequest(
            appointment_date=appointment_date + timedelta(days=1),
            start_time=start_time,
        )

        service = AppointmentService(db)

        with pytest.raises(ConflictException):
            service.reschedule_appointment(
                appointment_id=appointment.id,
                request=request,
            )

        db.refresh(appointment)

        assert appointment.appointment_date == original_date
        assert appointment.start_time == original_time
        assert appointment.status == original_status

    finally:
        db.rollback()
        db.close()
        
def test_cancel_appointment_success():
    db = SessionLocal()

    try:
        patient = get_patient(db)

        doctor, department, schedule = (
            get_active_doctor_with_schedule(db)
        )

        appointment_date = date.today() + timedelta(days=2)

        slot_duration = department.slot_duration_minutes
        start_time = schedule.start_time

        while start_time < schedule.end_time:
            end_datetime = (
                datetime.combine(
                    appointment_date,
                    start_time,
                )
                + timedelta(minutes=slot_duration)
            )

            if end_datetime.time() > schedule.end_time:
                break

            exists = db.scalar(
                select(Appointment.id)
                .where(
                    Appointment.doctor_id == doctor.id,
                    Appointment.appointment_date
                    == appointment_date,
                    Appointment.status
                    != AppointmentStatusEnum.CANCELLED,
                    Appointment.start_time
                    < end_datetime.time(),
                    Appointment.end_time
                    > start_time,
                )
            )

            if exists is None:
                break

            start_time = (
                datetime.combine(
                    appointment_date,
                    start_time,
                )
                + timedelta(minutes=slot_duration)
            ).time()
        else:
            pytest.skip(
                "No available appointment slot found."
            )

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            department_id=department.id,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_datetime.time(),
            status=AppointmentStatusEnum.CONFIRMED,
            reason="Cancel QA",
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        service = AppointmentService(db)

        request = AppointmentCancelRequest(
            cancelled_reason="ทดสอบการยกเลิกนัดหมาย",
        )

        result = service.cancel_appointment(
            appointment_id=appointment.id,
            request=request,
        )

        assert result.id == appointment.id
        assert result.status == (
            AppointmentStatusEnum.CANCELLED
        )
        assert result.cancelled_reason == (
            "ทดสอบการยกเลิกนัดหมาย"
        )
        assert result.cancelled_at is not None

        db.refresh(appointment)

        assert appointment.status == (
            AppointmentStatusEnum.CANCELLED
        )
        assert appointment.cancelled_reason == (
            "ทดสอบการยกเลิกนัดหมาย"
        )
        assert appointment.cancelled_at is not None

    finally:
        db.rollback()
        db.close()
        
def test_cancel_appointment_already_cancelled():
    db = SessionLocal()

    try:
        patient = get_patient(db)

        doctor, department, schedule = (
            get_active_doctor_with_schedule(db)
        )

        appointment_date = date.today() + timedelta(days=2)

        slot_duration = department.slot_duration_minutes
        start_time = schedule.start_time

        while start_time < schedule.end_time:
            end_datetime = (
                datetime.combine(
                    appointment_date,
                    start_time,
                )
                + timedelta(minutes=slot_duration)
            )

            if end_datetime.time() > schedule.end_time:
                break

            exists = db.scalar(
                select(Appointment.id)
                .where(
                    Appointment.doctor_id == doctor.id,
                    Appointment.appointment_date
                    == appointment_date,
                    Appointment.status
                    != AppointmentStatusEnum.CANCELLED,
                    Appointment.start_time
                    < end_datetime.time(),
                    Appointment.end_time
                    > start_time,
                )
            )

            if exists is None:
                break

            start_time = (
                datetime.combine(
                    appointment_date,
                    start_time,
                )
                + timedelta(minutes=slot_duration)
            ).time()
        else:
            pytest.skip(
                "No available appointment slot found."
            )

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            department_id=department.id,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_datetime.time(),
            status=AppointmentStatusEnum.CANCELLED,
            cancelled_reason="ยกเลิกก่อนทดสอบ",
            reason="Cancel Final Status QA",
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        original_status = appointment.status
        original_reason = appointment.cancelled_reason
        original_cancelled_at = appointment.cancelled_at

        request = AppointmentCancelRequest(
            cancelled_reason="พยายามยกเลิกซ้ำ",
        )

        service = AppointmentService(db)

        with pytest.raises(ConflictException):
            service.cancel_appointment(
                appointment_id=appointment.id,
                request=request,
            )

        db.refresh(appointment)

        assert appointment.status == original_status
        assert appointment.cancelled_reason == original_reason
        assert (
            appointment.cancelled_at
            == original_cancelled_at
        )

    finally:
        db.rollback()
        db.close()

def test_cancelled_appointment_slot_can_be_booked_again():
    db = SessionLocal()

    try:
        patient = get_patient(db)

        doctor, department, schedule = (
            get_active_doctor_with_schedule(db)
        )

        # หาอนาคตที่ตรงกับ weekday ของ Schedule
        appointment_date = date.today() + timedelta(days=1)

        while (
            appointment_date.strftime("%A").lower()
            != schedule.weekday.value
        ):
            appointment_date += timedelta(days=1)

        slot_duration = department.slot_duration_minutes
        start_time = schedule.start_time

        while start_time < schedule.end_time:
            end_datetime = (
                datetime.combine(
                    appointment_date,
                    start_time,
                )
                + timedelta(minutes=slot_duration)
            )

            if end_datetime.time() > schedule.end_time:
                break

            exists = db.scalar(
                select(Appointment.id)
                .where(
                    Appointment.doctor_id == doctor.id,
                    Appointment.appointment_date
                    == appointment_date,
                    Appointment.status
                    != AppointmentStatusEnum.CANCELLED,
                    Appointment.start_time
                    < end_datetime.time(),
                    Appointment.end_time
                    > start_time,
                )
            )

            if exists is None:
                break

            start_time = (
                datetime.combine(
                    appointment_date,
                    start_time,
                )
                + timedelta(minutes=slot_duration)
            ).time()
        else:
            pytest.skip(
                "No available appointment slot found."
            )

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            department_id=department.id,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_datetime.time(),
            status=AppointmentStatusEnum.CONFIRMED,
            reason="Cancel Slot Reuse QA",
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        cancel_request = AppointmentCancelRequest(
            cancelled_reason="ทดสอบคืน Slot",
        )

        service = AppointmentService(db)

        service.cancel_appointment(
            appointment_id=appointment.id,
            request=cancel_request,
        )

        db.expire_all()

        create_request = AppointmentCreateRequest(
            doctor_id=doctor.id,
            appointment_date=appointment_date,
            start_time=start_time,
            reason="Book Cancelled Slot QA",
        )

        result = service.create_appointment(
            patient_id=patient.id,
            request=create_request,
        )

        assert result is not None
        assert result.doctor_id == doctor.id
        assert result.appointment_date == appointment_date
        assert result.start_time == start_time
        assert result.status == (
            AppointmentStatusEnum.CONFIRMED
        )

    finally:
        db.rollback()
        db.close()

def test_cancel_appointment_creates_notification():
    db = SessionLocal()

    try:
        patient = get_patient(db)

        doctor, department, schedule = (
            get_active_doctor_with_schedule(db)
        )

        appointment_date = date.today() + timedelta(days=2)

        slot_duration = department.slot_duration_minutes
        start_time = schedule.start_time

        while start_time < schedule.end_time:
            end_datetime = (
                datetime.combine(
                    appointment_date,
                    start_time,
                )
                + timedelta(minutes=slot_duration)
            )

            if end_datetime.time() > schedule.end_time:
                break

            exists = db.scalar(
                select(Appointment.id)
                .where(
                    Appointment.doctor_id == doctor.id,
                    Appointment.appointment_date
                    == appointment_date,
                    Appointment.status
                    != AppointmentStatusEnum.CANCELLED,
                    Appointment.start_time
                    < end_datetime.time(),
                    Appointment.end_time
                    > start_time,
                )
            )

            if exists is None:
                break

            start_time = (
                datetime.combine(
                    appointment_date,
                    start_time,
                )
                + timedelta(minutes=slot_duration)
            ).time()
        else:
            pytest.skip(
                "No available appointment slot found."
            )

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            department_id=department.id,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_datetime.time(),
            status=AppointmentStatusEnum.CONFIRMED,
            reason="Cancel Notification QA",
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        request = AppointmentCancelRequest(
            cancelled_reason="ทดสอบ Notification การยกเลิก",
        )

        service = AppointmentService(db)

        service.cancel_appointment(
            appointment_id=appointment.id,
            request=request,
        )

        notification = db.scalar(
            select(NotificationLog)
            .where(
                NotificationLog.appointment_id
                == appointment.id,
                NotificationLog.patient_id
                == patient.id,
                NotificationLog.notification_type
                == NotificationTypeEnum.APPOINTMENT_CANCELLED,
            )
            .order_by(
                NotificationLog.sent_at.desc()
            )
        )

        assert notification is not None
        assert notification.appointment_id == appointment.id
        assert notification.patient_id == patient.id
        assert notification.notification_type == (
            NotificationTypeEnum.APPOINTMENT_CANCELLED
        )
        assert notification.notification_status == (
            NotificationStatusEnum.SENT
        )
        assert notification.sent_at is not None

    finally:
        db.rollback()
        db.close()

def test_check_in_success(monkeypatch):
    from app.models.appointment_qr_code import AppointmentQRCode
    from app.schemas.appointment_qr import AppointmentQRCodeCheckInRequest
    from app.services.appointment_qr import AppointmentQRCodeService

    db = SessionLocal()

    try:
        patient = get_patient(db)
        doctor, department, schedule = get_active_doctor_with_schedule(db)

        target_date = date.today() + timedelta(days=7)

        # หา date ที่ตรงกับ weekday ของ schedule
        schedule_weekday = schedule.weekday

        for _ in range(7):
            if target_date.strftime("%A").upper() == schedule_weekday.name:
                break

            target_date += timedelta(days=1)
        else:
            pytest.fail("Could not find a matching schedule weekday.")

        # หาเวลาที่ว่างจริงในวันนั้น
        existing_times = set(
            db.scalars(
                select(Appointment.start_time)
                .where(
                    Appointment.doctor_id == doctor.id,
                    Appointment.appointment_date == target_date,
                    Appointment.status != AppointmentStatusEnum.CANCELLED,
                )
            ).all()
        )

        appointment_start_time = schedule.start_time

        while appointment_start_time in existing_times:
            appointment_start_time = (
                datetime.combine(
                    target_date,
                    appointment_start_time,
                )
                + timedelta(
                    minutes=department.slot_duration_minutes
                )
            ).time()

            if appointment_start_time >= schedule.end_time:
                pytest.skip(
                    "No available appointment slot found."
                )

        appointment_start = datetime.combine(
            target_date,
            appointment_start_time,
        )

        end_time = (
            appointment_start
            + timedelta(
                minutes=department.slot_duration_minutes
            )
        ).time()

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            department_id=department.id,
            appointment_date=target_date,
            start_time=appointment_start_time,
            end_time=end_time,
            status=AppointmentStatusEnum.CONFIRMED,
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        qr_service = AppointmentQRCodeService(db)

        qr_response = qr_service.get_qr(
            appointment.id
        )

        request = AppointmentQRCodeCheckInRequest(
            token=qr_response.token
        )

        # จำลองเวลา 30 นาทีก่อนเวลานัด
        fake_now = appointment_start - timedelta(minutes=30)

        class FakeDateTime:
            @classmethod
            def now(cls, tz=None):
                return fake_now.replace(tzinfo=tz)

            @classmethod
            def combine(cls, *args, **kwargs):
                return datetime.combine(*args, **kwargs)

        import app.services.appointment_qr as qr_service_module

        monkeypatch.setattr(
            qr_service_module,
            "datetime",
            FakeDateTime,
        )

        response = qr_service.check_in(
            request=request,
            current_user=patient,
        )

        assert response.message == "Check-in successful."

        db.refresh(appointment)

        qr_code = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id
            )
        )

        assert appointment.status == AppointmentStatusEnum.CHECKED_IN
        assert qr_code is not None
        assert qr_code.is_used is True
        assert qr_code.used_at is not None

    finally:
        db.rollback()
        db.close()

def create_check_in_test_appointment(db):
    from app.models.appointment_qr_code import AppointmentQRCode
    from app.services.appointment_qr import AppointmentQRCodeService

    patient = get_patient(db)

    doctor, department, schedule = (
        get_active_doctor_with_schedule(db)
    )

    slot_duration = department.slot_duration_minutes

    # ค้นหาวันที่ตรงกับ schedule ภายใน 30 วัน
    for day_offset in range(7, 38):
        target_date = date.today() + timedelta(days=day_offset)

        if (
            target_date.strftime("%A").upper()
            != schedule.weekday.name
        ):
            continue

        # ค้นหา slot ที่ว่างจริงในวันนั้น
        appointment_start_time = schedule.start_time

        while appointment_start_time < schedule.end_time:
            appointment_end_time = (
                datetime.combine(
                    target_date,
                    appointment_start_time,
                )
                + timedelta(minutes=slot_duration)
            )

            if appointment_end_time.time() > schedule.end_time:
                break

            exists = db.scalar(
                select(Appointment.id)
                .where(
                    Appointment.doctor_id == doctor.id,
                    Appointment.appointment_date == target_date,
                    Appointment.status
                    != AppointmentStatusEnum.CANCELLED,
                    Appointment.start_time
                    < appointment_end_time.time(),
                    Appointment.end_time
                    > appointment_start_time,
                )
            )

            if exists is None:
                break

            appointment_start_time = appointment_end_time.time()

        else:
            continue

        appointment_start = datetime.combine(
            target_date,
            appointment_start_time,
        )

        appointment_end = (
            appointment_start
            + timedelta(minutes=slot_duration)
        )

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            department_id=department.id,
            appointment_date=target_date,
            start_time=appointment_start_time,
            end_time=appointment_end.time(),
            status=AppointmentStatusEnum.CONFIRMED,
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        qr_service = AppointmentQRCodeService(db)

        qr_response = qr_service.get_qr(
            appointment.id
        )

        qr_code = db.scalar(
            select(AppointmentQRCode)
            .where(
                AppointmentQRCode.appointment_id
                == appointment.id
            )
        )

        return (
            patient,
            appointment,
            qr_service,
            qr_response.token,
            appointment_start,
            qr_code,
        )

    pytest.skip(
        "No available appointment slot found within 30 days."
    )
    
    
def test_check_in_already_used(monkeypatch):
    from app.schemas.appointment_qr import AppointmentQRCodeCheckInRequest
    from app.services.appointment_qr import AppointmentQRCodeService
    from app.core.exceptions import AppointmentQRCodeAlreadyUsedException

    db = SessionLocal()

    try:
        (
            patient,
            appointment,
            qr_service,
            token,
            appointment_start,
            qr_code,
        ) = create_check_in_test_appointment(db)

        class FakeDateTime:
            @classmethod
            def now(cls, tz=None):
                return appointment_start.replace(tzinfo=tz) - timedelta(
                    minutes=30
                )

            @classmethod
            def combine(cls, *args, **kwargs):
                return datetime.combine(*args, **kwargs)

        import app.services.appointment_qr as qr_service_module

        monkeypatch.setattr(
            qr_service_module,
            "datetime",
            FakeDateTime,
        )

        request = AppointmentQRCodeCheckInRequest(
            token=token
        )

        qr_service.check_in(
            request=request,
            current_user=patient,
        )

        with pytest.raises(AppointmentQRCodeAlreadyUsedException):
            qr_service.check_in(
                request=request,
                current_user=patient,
            )

    finally:
        db.rollback()
        db.close()


def test_check_in_cancelled_appointment(monkeypatch):
    from app.schemas.appointment_qr import AppointmentQRCodeCheckInRequest
    from app.services.appointment_qr import AppointmentQRCodeService
    from app.core.exceptions import CannotCheckInCancelledAppointmentException

    db = SessionLocal()

    try:
        (
            patient,
            appointment,
            qr_service,
            token,
            appointment_start,
            qr_code,
        ) = create_check_in_test_appointment(db)

        appointment.status = AppointmentStatusEnum.CANCELLED
        db.commit()

        request = AppointmentQRCodeCheckInRequest(
            token=token
        )

        with pytest.raises(CannotCheckInCancelledAppointmentException):
            qr_service.check_in(
                request=request,
                current_user=patient,
            )

    finally:
        db.rollback()
        db.close()


@pytest.mark.parametrize(
    "status",
    [
        AppointmentStatusEnum.COMPLETED,
        AppointmentStatusEnum.NO_SHOW,
    ],
)
def test_check_in_final_appointment_status(status):
    from app.schemas.appointment_qr import AppointmentQRCodeCheckInRequest
    from app.core.exceptions import CannotGenerateAppointmentQRCodeException

    db = SessionLocal()

    try:
        (
            patient,
            appointment,
            qr_service,
            token,
            appointment_start,
            qr_code,
        ) = create_check_in_test_appointment(db)

        appointment.status = status
        db.commit()

        request = AppointmentQRCodeCheckInRequest(
            token=token
        )

        with pytest.raises(CannotGenerateAppointmentQRCodeException):
            qr_service.check_in(
                request=request,
                current_user=patient,
            )

    finally:
        db.rollback()
        db.close()


def test_check_in_too_early(monkeypatch):
    from app.schemas.appointment_qr import AppointmentQRCodeCheckInRequest

    db = SessionLocal()

    try:
        (
            patient,
            appointment,
            qr_service,
            token,
            appointment_start,
            qr_code,
        ) = create_check_in_test_appointment(db)

        fake_now = appointment_start - timedelta(
            hours=1,
            minutes=1,
        )

        class FakeDateTime:
            @classmethod
            def now(cls, tz=None):
                return fake_now.replace(tzinfo=tz)

            @classmethod
            def combine(cls, *args, **kwargs):
                return datetime.combine(*args, **kwargs)

        import app.services.appointment_qr as qr_service_module

        monkeypatch.setattr(
            qr_service_module,
            "datetime",
            FakeDateTime,
        )

        request = AppointmentQRCodeCheckInRequest(
            token=token
        )

        with pytest.raises(ConflictException):
            qr_service.check_in(
                request=request,
                current_user=patient,
            )

    finally:
        db.rollback()
        db.close()


def test_check_in_expired_sets_no_show(monkeypatch):
    from app.schemas.appointment_qr import AppointmentQRCodeCheckInRequest
    from app.core.exceptions import AppointmentQRCodeExpiredException

    db = SessionLocal()

    try:
        (
            patient,
            appointment,
            qr_service,
            token,
            appointment_start,
            qr_code,
        ) = create_check_in_test_appointment(db)

        fake_now = appointment_start + timedelta(
            minutes=16
        )

        class FakeDateTime:
            @classmethod
            def now(cls, tz=None):
                return fake_now.replace(tzinfo=tz)

            @classmethod
            def combine(cls, *args, **kwargs):
                return datetime.combine(*args, **kwargs)

        import app.services.appointment_qr as qr_service_module

        monkeypatch.setattr(
            qr_service_module,
            "datetime",
            FakeDateTime,
        )

        request = AppointmentQRCodeCheckInRequest(
            token=token
        )

        with pytest.raises(AppointmentQRCodeExpiredException):
            qr_service.check_in(
                request=request,
                current_user=patient,
            )

        db.refresh(appointment)

        assert appointment.status == AppointmentStatusEnum.NO_SHOW
        assert qr_code.is_used is False

    finally:
        db.rollback()
        db.close()