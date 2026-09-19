import uuid

import pytest
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.exceptions import (
    ForbiddenException,
    NotFoundException,
    ConflictException,
    MedicalRecordAppointmentNotCheckedInException
)
from app.core.enums import UserRoleEnum
from app.models.medical_record import MedicalRecord
from app.services.medical_record import MedicalRecordService
from datetime import date, datetime, timedelta

from app.core.enums import AppointmentStatusEnum
from app.models.appointment import Appointment
from app.models.department import Department
from app.models.doctor import Doctor
from app.models.doctor_schedule_template import DoctorScheduleTemplate
from app.models.user import User
from app.schemas.medical_record_schema import MedicalRecordCreate
from app.schemas.medical_record_schema import MedicalRecordUpdate

def get_medical_record(db):
    medical_record = db.scalar(
        select(MedicalRecord)
        .order_by(MedicalRecord.created_at.desc())
    )

    if medical_record is None:
        pytest.skip("No medical record found.")

    return medical_record


def get_another_medical_record(
    db,
    medical_record,
):
    another_record = db.scalar(
        select(MedicalRecord)
        .where(
            MedicalRecord.id != medical_record.id,
            MedicalRecord.doctor_id
            != medical_record.doctor_id,
        )
        .order_by(
            MedicalRecord.created_at.desc()
        )
    )

    if another_record is None:
        pytest.skip(
            "No medical record from another doctor found."
        )

    return another_record


def test_get_medical_record_patient_own_record():
    db = SessionLocal()

    try:
        medical_record = get_medical_record(db)

        service = MedicalRecordService(db)

        result = service.get_medical_record(
            medical_record.id,
            patient_id=medical_record.patient_id,
        )

        assert result is not None
        assert result.id == medical_record.id
        assert result.appointment_id == (
            medical_record.appointment_id
        )
        assert result.patient_id == (
            medical_record.patient_id
        )
        assert result.doctor_id == (
            medical_record.doctor_id
        )
        assert result.chief_complaint == (
            medical_record.chief_complaint
        )
        assert result.diagnosis == (
            medical_record.diagnosis
        )

    finally:
        db.rollback()
        db.close()


def test_get_medical_record_patient_other_record_forbidden():
    db = SessionLocal()

    try:
        medical_record = get_medical_record(db)

        other_patient_record = db.scalar(
            select(MedicalRecord)
            .where(
                MedicalRecord.patient_id
                != medical_record.patient_id,
            )
            .order_by(
                MedicalRecord.created_at.desc()
            )
        )

        if other_patient_record is None:
            pytest.skip(
                "No medical record from another patient found."
            )

        service = MedicalRecordService(db)

        with pytest.raises(ForbiddenException):
            service.get_medical_record(
                other_patient_record.id,
                patient_id=medical_record.patient_id,
            )

    finally:
        db.rollback()
        db.close()


def test_get_medical_record_doctor_own_record():
    db = SessionLocal()

    try:
        medical_record = get_medical_record(db)

        service = MedicalRecordService(db)

        result = service.get_medical_record(
            medical_record.id,
            doctor_id=medical_record.doctor_id,
        )

        assert result is not None
        assert result.id == medical_record.id
        assert result.appointment_id == (
            medical_record.appointment_id
        )
        assert result.patient_id == (
            medical_record.patient_id
        )
        assert result.doctor_id == (
            medical_record.doctor_id
        )
        assert result.chief_complaint == (
            medical_record.chief_complaint
        )
        assert result.diagnosis == (
            medical_record.diagnosis
        )

    finally:
        db.rollback()
        db.close()


def test_get_medical_record_doctor_other_record_forbidden():
    db = SessionLocal()

    try:
        medical_record = get_medical_record(db)

        other_record = get_another_medical_record(
            db,
            medical_record,
        )

        service = MedicalRecordService(db)

        with pytest.raises(ForbiddenException):
            service.get_medical_record(
                other_record.id,
                doctor_id=medical_record.doctor_id,
            )

    finally:
        db.rollback()
        db.close()


def test_get_medical_record_not_found():
    db = SessionLocal()

    try:
        service = MedicalRecordService(db)

        medical_record_id = uuid.uuid4()

        with pytest.raises(NotFoundException):
            service.get_medical_record(
                medical_record_id,
            )

    finally:
        db.rollback()
        db.close()


def test_get_patient_medical_records():
    db = SessionLocal()

    try:
        medical_record = get_medical_record(db)

        service = MedicalRecordService(db)

        result = service.get_patient_medical_records(
            medical_record.patient_id,
        )

        assert result
        assert all(
            record.patient_id
            == medical_record.patient_id
            for record in result
        )

        expected_ids = {
            record.id
            for record in db.scalars(
                select(MedicalRecord)
                .where(
                    MedicalRecord.patient_id
                    == medical_record.patient_id,
                )
            ).all()
        }

        result_ids = {
            record.id
            for record in result
        }

        assert result_ids == expected_ids

    finally:
        db.rollback()
        db.close()


def test_get_patient_medical_records_ordered_by_created_at_desc():
    db = SessionLocal()

    try:
        medical_record = get_medical_record(db)

        service = MedicalRecordService(db)

        result = service.get_patient_medical_records(
            medical_record.patient_id,
        )

        if len(result) < 2:
            pytest.skip(
                "Need at least 2 medical records "
                "for ordering test."
            )

        created_at_values = [
            record.created_at
            for record in result
        ]

        assert created_at_values == sorted(
            created_at_values,
            reverse=True,
        )

    finally:
        db.rollback()
        db.close()

def get_test_patient(db):
    patient = db.scalar(
        select(User)
        .where(
            User.role == UserRoleEnum.PATIENT,
        )
        .limit(1)
    )

    if patient is None:
        pytest.skip("No patient found.")

    return patient


def get_test_doctor_with_department(db):
    row = db.execute(
        select(
            Doctor,
            Department,
        )
        .join(
            Department,
            Doctor.department_id == Department.id,
        )
        .limit(1)
    ).first()

    if row is None:
        pytest.skip(
            "No doctor with department found."
        )

    return row


def get_checked_in_appointment(db):
    appointment = db.scalar(
        select(Appointment)
        .where(
            Appointment.status
            == AppointmentStatusEnum.CHECKED_IN,
        )
        .order_by(
            Appointment.appointment_date.desc(),
            Appointment.start_time.desc(),
        )
    )

    if appointment is None:
        pytest.skip(
            "No checked-in appointment found."
        )

    return appointment


def test_create_medical_record_success():
    db = SessionLocal()

    try:
        appointment = get_checked_in_appointment(db)

        existing_record = db.scalar(
            select(MedicalRecord)
            .where(
                MedicalRecord.appointment_id
                == appointment.id,
            )
        )

        if existing_record is not None:
            pytest.skip(
                "Selected appointment already has "
                "a medical record."
            )

        service = MedicalRecordService(db)

        request = MedicalRecordCreate(
            appointment_id=appointment.id,
            chief_complaint="Automated QA",
            present_illness="QA test present illness",
            physical_examination="QA test examination",
            diagnosis="QA test diagnosis",
            treatment="QA test treatment",
            recommendation="QA test recommendation",
            note="QA test note",
        )

        result = service.create_medical_record(
            doctor_id=appointment.doctor_id,
            request=request,
        )

        assert result is not None
        assert result.appointment_id == appointment.id
        assert result.patient_id == appointment.patient_id
        assert result.doctor_id == appointment.doctor_id
        assert result.chief_complaint == "Automated QA"
        assert result.present_illness == (
            "QA test present illness"
        )
        assert result.physical_examination == (
            "QA test examination"
        )
        assert result.diagnosis == "QA test diagnosis"
        assert result.treatment == "QA test treatment"
        assert result.recommendation == (
            "QA test recommendation"
        )
        assert result.note == "QA test note"

        db.refresh(appointment)

        assert appointment.status == (
            AppointmentStatusEnum.COMPLETED
        )

        saved_record = db.scalar(
            select(MedicalRecord)
            .where(
                MedicalRecord.id == result.id,
            )
        )

        assert saved_record is not None
        assert saved_record.appointment_id == appointment.id
        assert saved_record.patient_id == appointment.patient_id
        assert saved_record.doctor_id == appointment.doctor_id

    finally:
        db.rollback()
        db.close()


def test_create_medical_record_not_checked_in():
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment)
            .where(
                Appointment.status.notin_(
                    [
                        AppointmentStatusEnum.CHECKED_IN,
                        AppointmentStatusEnum.IN_PROGRESS,
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
                "No appointment with non checked-in status found."
            )

        existing_record = db.scalar(
            select(MedicalRecord)
            .where(
                MedicalRecord.appointment_id
                == appointment.id,
            )
        )

        if existing_record is not None:
            pytest.skip(
                "Selected appointment already has "
                "a medical record."
            )

        service = MedicalRecordService(db)

        request = MedicalRecordCreate(
            appointment_id=appointment.id,
            chief_complaint="Automated QA",
            diagnosis="QA test diagnosis",
        )

        with pytest.raises(
            MedicalRecordAppointmentNotCheckedInException
        ):
            service.create_medical_record(
                doctor_id=appointment.doctor_id,
                request=request,
            )

    finally:
        db.rollback()
        db.close()


def test_create_medical_record_wrong_doctor():
    db = SessionLocal()

    try:
        appointment = get_checked_in_appointment(db)

        existing_record = db.scalar(
            select(MedicalRecord)
            .where(
                MedicalRecord.appointment_id
                == appointment.id,
            )
        )

        if existing_record is not None:
            pytest.skip(
                "Selected appointment already has "
                "a medical record."
            )

        other_doctor = db.scalar(
            select(Doctor)
            .where(
                Doctor.id != appointment.doctor_id,
            )
        )

        if other_doctor is None:
            pytest.skip(
                "No second doctor found."
            )

        service = MedicalRecordService(db)

        request = MedicalRecordCreate(
            appointment_id=appointment.id,
            chief_complaint="Automated QA",
            diagnosis="QA test diagnosis",
        )

        with pytest.raises(ConflictException):
            service.create_medical_record(
                doctor_id=other_doctor.id,
                request=request,
            )

    finally:
        db.rollback()
        db.close()


def test_create_medical_record_appointment_not_found():
    db = SessionLocal()

    try:
        service = MedicalRecordService(db)

        request = MedicalRecordCreate(
            appointment_id=uuid.uuid4(),
            chief_complaint="Automated QA",
            diagnosis="QA test diagnosis",
        )

        with pytest.raises(NotFoundException):
            service.create_medical_record(
                doctor_id=uuid.uuid4(),
                request=request,
            )

    finally:
        db.rollback()
        db.close()


def test_create_medical_record_duplicate():
    db = SessionLocal()

    try:
        existing_record = get_medical_record(db)

        appointment = db.get(
            Appointment,
            existing_record.appointment_id,
        )

        if appointment is None:
            pytest.skip(
                "Appointment for medical record not found."
            )

        # Medical Record ที่มีอยู่จริงต้องถูกตรวจ duplicate
        # หลังจากผ่านเงื่อนไข CHECKED_IN ก่อน
        appointment.status = (
            AppointmentStatusEnum.CHECKED_IN
        )

        service = MedicalRecordService(db)

        request = MedicalRecordCreate(
            appointment_id=appointment.id,
            chief_complaint="Duplicate QA",
            diagnosis="Duplicate QA diagnosis",
        )

        with pytest.raises(ConflictException):
            service.create_medical_record(
                doctor_id=existing_record.doctor_id,
                request=request,
            )

    finally:
        db.rollback()
        db.close()

def test_update_medical_record_success():
    db = SessionLocal()

    try:
        medical_record = get_medical_record(db)

        service = MedicalRecordService(db)

        original_chief_complaint = (
            medical_record.chief_complaint
        )
        original_diagnosis = medical_record.diagnosis

        request = MedicalRecordUpdate(
            chief_complaint="Updated QA Chief Complaint",
            diagnosis="Updated QA Diagnosis",
        )

        result = service.update_medical_record(
            medical_record_id=medical_record.id,
            doctor_id=medical_record.doctor_id,
            request=request,
        )

        assert result is not None
        assert result.id == medical_record.id
        assert result.chief_complaint == (
            "Updated QA Chief Complaint"
        )
        assert result.diagnosis == (
            "Updated QA Diagnosis"
        )

        db.refresh(medical_record)

        assert medical_record.chief_complaint == (
            "Updated QA Chief Complaint"
        )
        assert medical_record.diagnosis == (
            "Updated QA Diagnosis"
        )

        assert original_chief_complaint != (
            medical_record.chief_complaint
        )
        assert original_diagnosis != (
            medical_record.diagnosis
        )

    finally:
        db.rollback()
        db.close()


def test_update_medical_record_partial_update():
    db = SessionLocal()

    try:
        medical_record = get_medical_record(db)

        service = MedicalRecordService(db)

        original_diagnosis = medical_record.diagnosis
        original_treatment = medical_record.treatment

        request = MedicalRecordUpdate(
            treatment="Updated QA Treatment",
        )

        result = service.update_medical_record(
            medical_record_id=medical_record.id,
            doctor_id=medical_record.doctor_id,
            request=request,
        )

        assert result is not None
        assert result.id == medical_record.id
        assert result.treatment == (
            "Updated QA Treatment"
        )

        # Field ที่ไม่ได้ส่งมา ต้องไม่ถูกเปลี่ยน
        assert result.diagnosis == original_diagnosis

        db.refresh(medical_record)

        assert medical_record.treatment == (
            "Updated QA Treatment"
        )
        assert medical_record.diagnosis == original_diagnosis

        # ป้องกันกรณีข้อมูลเดิมบังเอิญตรงกับค่าที่ Test กำหนด
        assert original_treatment != (
            medical_record.treatment
        )

    finally:
        db.rollback()
        db.close()


def test_update_medical_record_other_doctor_forbidden():
    db = SessionLocal()

    try:
        medical_record = get_medical_record(db)

        other_record = db.scalar(
            select(MedicalRecord)
            .where(
                MedicalRecord.id != medical_record.id,
                MedicalRecord.doctor_id
                != medical_record.doctor_id,
            )
            .order_by(
                MedicalRecord.created_at.desc()
            )
        )

        if other_record is None:
            pytest.skip(
                "No medical record from another doctor found."
            )

        other_doctor_id = other_record.doctor_id

        service = MedicalRecordService(db)

        request = MedicalRecordUpdate(
            diagnosis="Unauthorized QA Update",
        )

        with pytest.raises(ForbiddenException):
            service.update_medical_record(
                medical_record_id=medical_record.id,
                doctor_id=other_doctor_id,
                request=request,
            )

        db.refresh(medical_record)

        # ต้องไม่เปลี่ยนข้อมูลเมื่อถูกปฏิเสธ
        assert medical_record.diagnosis != (
            "Unauthorized QA Update"
        )

    finally:
        db.rollback()
        db.close()


def test_update_medical_record_not_found():
    db = SessionLocal()

    try:
        service = MedicalRecordService(db)

        request = MedicalRecordUpdate(
            diagnosis="Not Found QA Update",
        )

        with pytest.raises(NotFoundException):
            service.update_medical_record(
                medical_record_id=uuid.uuid4(),
                doctor_id=uuid.uuid4(),
                request=request,
            )

    finally:
        db.rollback()
        db.close()
        
def test_create_medical_record_empty_chief_complaint_validation():
    with pytest.raises(ValueError):
        MedicalRecordCreate(
            appointment_id=uuid.uuid4(),
            chief_complaint="",
            diagnosis="QA test diagnosis",
        )

def test_create_medical_record_empty_diagnosis_validation():
    with pytest.raises(ValueError):
        MedicalRecordCreate(
            appointment_id=uuid.uuid4(),
            chief_complaint="QA test chief complaint",
            diagnosis="",
        )

def test_update_medical_record_empty_diagnosis_validation():
    with pytest.raises(ValueError):
        MedicalRecordUpdate(
            diagnosis="",
        )

def test_update_medical_record_empty_chief_complaint_validation():
    with pytest.raises(ValueError):
        MedicalRecordUpdate(
            chief_complaint="",
        )

def test_update_medical_record_empty_update():
    db = SessionLocal()

    try:
        medical_record = get_medical_record(db)

        service = MedicalRecordService(db)

        original_chief_complaint = (
            medical_record.chief_complaint
        )
        original_diagnosis = medical_record.diagnosis
        original_treatment = medical_record.treatment

        request = MedicalRecordUpdate()

        result = service.update_medical_record(
            medical_record_id=medical_record.id,
            doctor_id=medical_record.doctor_id,
            request=request,
        )

        assert result is not None
        assert result.id == medical_record.id

        assert result.chief_complaint == (
            original_chief_complaint
        )
        assert result.diagnosis == original_diagnosis
        assert result.treatment == original_treatment

    finally:
        db.rollback()
        db.close()