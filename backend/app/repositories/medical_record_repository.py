from __future__ import annotations

import uuid

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord


class MedicalRecordRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        medical_record: MedicalRecord,
    ) -> MedicalRecord:
        self.db.add(medical_record)
        self.db.flush()
        self.db.refresh(medical_record)
        return medical_record

    def get_by_id(
        self,
        medical_record_id: uuid.UUID,
    ) -> MedicalRecord | None:
        stmt: Select = select(MedicalRecord).where(
            MedicalRecord.id == medical_record_id
        )

        return self.db.scalar(stmt)

    def get_by_appointment_id(
        self,
        appointment_id: uuid.UUID,
    ) -> MedicalRecord | None:
        stmt: Select = select(MedicalRecord).where(
            MedicalRecord.appointment_id == appointment_id
        )

        return self.db.scalar(stmt)

    def get_by_patient(
        self,
        patient_id: uuid.UUID,
    ) -> list[MedicalRecord]:
        stmt: Select = (
            select(MedicalRecord)
            .where(MedicalRecord.patient_id == patient_id)
            .order_by(
                MedicalRecord.created_at.desc(),
            )
        )

        return list(self.db.scalars(stmt).all())

    def get_by_doctor_and_date_range(
        self,
        doctor_id: uuid.UUID,
        date_from=None,
        date_to=None,
    ) -> list[MedicalRecord]:
        stmt: Select = (
            select(MedicalRecord)
            .join(
                Appointment,
                MedicalRecord.appointment_id == Appointment.id,
            )
            .where(
                MedicalRecord.doctor_id == doctor_id,
            )
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        if date_from is not None:
            stmt = stmt.where(
                Appointment.appointment_date >= date_from,
            )

        if date_to is not None:
            stmt = stmt.where(
                Appointment.appointment_date <= date_to,
            )

        return list(self.db.scalars(stmt).all())

    def update(
        self,
        medical_record: MedicalRecord,
    ) -> MedicalRecord:
        self.db.flush()
        self.db.refresh(medical_record)
        return medical_record