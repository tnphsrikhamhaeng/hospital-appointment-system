import uuid
from unittest.mock import patch

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.enums import AppointmentStatusEnum
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.services.medical_record import MedicalRecordService

from app.schemas.medical_record_schema import (
    MedicalRecordCreate,
    MedicalRecordUpdate,
)

def test_create_medical_record():
    db = SessionLocal()

    try:
        appointment = db.scalar(
          select(Appointment)
          .where(
              Appointment.status
              == AppointmentStatusEnum.CHECKED_IN,
              ~Appointment.id.in_(
                  select(MedicalRecord.appointment_id)
              ),
          )
      )

        if appointment is None:
            print(
                "TEST FAILED: "
                "No CHECKED_IN appointment found."
            )
            return

        existing_record = db.scalar(
            select(MedicalRecord)
            .where(
                MedicalRecord.appointment_id
                == appointment.id
            )
        )

        if existing_record is not None:
            print(
                "TEST FAILED: "
                "Appointment already has a medical record."
            )
            return

        service = MedicalRecordService(db)

        request = MedicalRecordCreate(
            appointment_id=appointment.id,
            chief_complaint="มีไข้และปวดศีรษะ",
            present_illness="มีอาการมา 3 วัน",
            physical_examination="Temperature 38.5 C",
            diagnosis="Common Cold",
            treatment="ให้ยาลดไข้",
            recommendation="พักผ่อนและดื่มน้ำมาก ๆ",
            note="Service test",
        )

        with patch.object(
            db,
            "commit",
            side_effect=db.flush,
        ):
            result = service.create_medical_record(
                doctor_id=appointment.doctor_id,
                request=request,
            )

        print("CREATE MEDICAL RECORD PASSED")
        print("Medical Record ID:", result.id)

        assert result.appointment_id == appointment.id
        assert result.patient_id == appointment.patient_id
        assert result.doctor_id == appointment.doctor_id
        assert result.diagnosis == "Common Cold"

        assert (
            appointment.status
            == AppointmentStatusEnum.COMPLETED
        )

        print("APPOINTMENT STATUS UPDATE PASSED")

        db.rollback()

        print("ROLLBACK PASSED")

    except Exception as error:
        db.rollback()

        print("TEST FAILED")
        print(type(error).__name__)
        print(error)

    finally:
        db.close()


def test_wrong_doctor():

    db = SessionLocal()

    try:
        appointment = db.scalar(
        select(Appointment)
        .where(
            Appointment.status
            == AppointmentStatusEnum.CHECKED_IN,
            ~Appointment.id.in_(
                select(MedicalRecord.appointment_id)
            ),
        )
    )

        if appointment is None:
            print(
                "WRONG DOCTOR TEST SKIPPED: "
                "No CHECKED_IN appointment found."
            )
            return

        existing_record = db.scalar(
            select(MedicalRecord)
            .where(
                MedicalRecord.appointment_id
                == appointment.id
            )
        )

        if existing_record is not None:
            print(
                "WRONG DOCTOR TEST SKIPPED: "
                "Appointment already has a medical record."
            )
            return

        service = MedicalRecordService(db)

        request = MedicalRecordCreate(
            appointment_id=appointment.id,
            chief_complaint="Test",
            diagnosis="Test Diagnosis",
        )

        wrong_doctor_id = uuid.uuid4()

        try:
            service.create_medical_record(
                doctor_id=wrong_doctor_id,
                request=request,
            )

            print("WRONG DOCTOR TEST FAILED")

        except Exception as error:
            print("WRONG DOCTOR TEST PASSED")
            print(type(error).__name__)

        db.rollback()

    finally:
        db.close()
        
def test_appointment_not_found():
    db = SessionLocal()

    try:
        service = MedicalRecordService(db)

        request = MedicalRecordCreate(
            appointment_id=uuid.uuid4(),
            chief_complaint="Test",
            diagnosis="Test Diagnosis",
        )

        try:
            service.create_medical_record(
                doctor_id=uuid.uuid4(),
                request=request,
            )

            print("APPOINTMENT NOT FOUND TEST FAILED")

        except Exception as error:
            print("APPOINTMENT NOT FOUND TEST PASSED")
            print(type(error).__name__)

    finally:
        db.close()
        
def test_appointment_not_checked_in():
    db = SessionLocal()

    try:
        appointment = db.scalar(
            select(Appointment).where(
                Appointment.status
                != AppointmentStatusEnum.CHECKED_IN
            )
        )

        if appointment is None:
            print(
                "NOT CHECKED_IN TEST SKIPPED: "
                "No suitable appointment found."
            )
            return

        existing_record = db.scalar(
            select(MedicalRecord).where(
                MedicalRecord.appointment_id
                == appointment.id
            )
        )

        if existing_record is not None:
            print(
                "NOT CHECKED_IN TEST SKIPPED: "
                "Appointment already has a medical record."
            )
            return

        service = MedicalRecordService(db)

        request = MedicalRecordCreate(
            appointment_id=appointment.id,
            chief_complaint="Test",
            diagnosis="Test Diagnosis",
        )

        try:
            service.create_medical_record(
                doctor_id=appointment.doctor_id,
                request=request,
            )

            print(
                "NOT CHECKED_IN TEST FAILED"
            )

        except Exception as error:
            print(
                "NOT CHECKED_IN TEST PASSED"
            )
            print(type(error).__name__)

        db.rollback()

    finally:
        db.close()
        
        
def test_duplicate_medical_record():
    db = SessionLocal()

    try:
        medical_record = create_test_medical_record(db)

        if medical_record is None:
            print(
                "DUPLICATE TEST SKIPPED: "
                "No CHECKED_IN appointment found."
            )
            return

        appointment = db.scalar(
            select(Appointment).where(
                Appointment.id
                == medical_record.appointment_id
            )
        )

        service = MedicalRecordService(db)

        request = MedicalRecordCreate(
            appointment_id=appointment.id,
            chief_complaint="Duplicate Test",
            diagnosis="Duplicate Diagnosis",
        )

        try:
            service.create_medical_record(
                doctor_id=appointment.doctor_id,
                request=request,
            )

            print(
                "DUPLICATE MEDICAL RECORD TEST FAILED"
            )

        except Exception as error:
            print(
                "DUPLICATE MEDICAL RECORD TEST PASSED"
            )
            print(type(error).__name__)

        db.rollback()

    finally:
        db.close()
        
        
def test_get_medical_record():
    db = SessionLocal()

    try:
        medical_record = db.scalar(
            select(MedicalRecord)
        )

        if medical_record is None:
            print(
                "GET MEDICAL RECORD TEST SKIPPED: "
                "No medical record found."
            )
            return

        service = MedicalRecordService(db)

        result = service.get_medical_record(
            medical_record.id
        )

        assert result.id == medical_record.id
        assert (
            result.appointment_id
            == medical_record.appointment_id
        )
        assert (
            result.patient_id
            == medical_record.patient_id
        )
        assert (
            result.doctor_id
            == medical_record.doctor_id
        )

        print("GET MEDICAL RECORD PASSED")

    finally:
        db.close()

def test_update_medical_record():
    db = SessionLocal()

    try:
        medical_record = db.scalar(
            select(MedicalRecord)
        )

        if medical_record is None:
            print(
                "UPDATE MEDICAL RECORD TEST SKIPPED: "
                "No medical record found."
            )
            return

        service = MedicalRecordService(db)

        request = MedicalRecordUpdate(
            diagnosis="Updated Diagnosis",
            note="Updated by service test",
        )

        result = service.update_medical_record(
            medical_record.id,
            request,
        )

        assert result.diagnosis == "Updated Diagnosis"
        assert result.note == "Updated by service test"

        print("UPDATE MEDICAL RECORD PASSED")

        db.rollback()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
        
        
def create_test_medical_record(db):
    appointment = db.scalar(
        select(Appointment)
        .where(
            Appointment.status
            == AppointmentStatusEnum.CHECKED_IN
        )
    )

    if appointment is None:
        return None

    existing_record = db.scalar(
        select(MedicalRecord)
        .where(
            MedicalRecord.appointment_id
            == appointment.id
        )
    )

    if existing_record is not None:
        return existing_record

    medical_record = MedicalRecord(
        appointment_id=appointment.id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        chief_complaint="Test Chief Complaint",
        diagnosis="Test Diagnosis",
        note="Temporary test record",
    )

    db.add(medical_record)
    db.flush()
    db.refresh(medical_record)

    return medical_record
  
  
def test_get_patient_medical_records():
    db = SessionLocal()

    try:
        medical_record = create_test_medical_record(db)

        if medical_record is None:
            print(
                "GET PATIENT MEDICAL RECORDS TEST SKIPPED: "
                "No CHECKED_IN appointment found."
            )
            return

        service = MedicalRecordService(db)

        results = service.get_patient_medical_records(
            medical_record.patient_id
        )

        assert len(results) >= 1

        assert any(
            record.id == medical_record.id
            for record in results
        )

        print(
            "GET PATIENT MEDICAL RECORDS PASSED"
        )

        db.rollback()

    finally:
        db.close()
        
        
        
def test_update_medical_record():
    db = SessionLocal()

    try:
        medical_record = create_test_medical_record(db)

        if medical_record is None:
            print(
                "UPDATE MEDICAL RECORD TEST SKIPPED: "
                "No CHECKED_IN appointment found."
            )
            return

        service = MedicalRecordService(db)

        request = MedicalRecordUpdate(
            diagnosis="Updated Diagnosis",
            note="Updated by service test",
        )

        result = service.update_medical_record(
            medical_record.id,
            request,
        )

        assert result.diagnosis == "Updated Diagnosis"
        assert result.note == "Updated by service test"

        print("UPDATE MEDICAL RECORD PASSED")

        db.rollback()

    finally:
        db.close()
        
        
def test_update_medical_record_not_found():
    db = SessionLocal()

    try:
        service = MedicalRecordService(db)

        request = MedicalRecordUpdate(
            diagnosis="Test",
        )

        try:
            service.update_medical_record(
                uuid.uuid4(),
                request,
            )

            print(
                "UPDATE NOT FOUND TEST FAILED"
            )

        except Exception as error:
            print(
                "UPDATE NOT FOUND TEST PASSED"
            )
            print(type(error).__name__)

    finally:
        db.close()


if __name__ == "__main__":
    test_create_medical_record()
    test_wrong_doctor()

    test_appointment_not_found()
    test_appointment_not_checked_in()

    test_duplicate_medical_record()

    test_get_medical_record()
    test_get_patient_medical_records()

    test_update_medical_record()
    test_update_medical_record_not_found()