from __future__ import annotations

import uuid
from datetime import date, time

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment


class AppointmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        appointment: Appointment,
    ) -> Appointment:
        self.db.add(appointment)
        self.db.flush()
        self.db.refresh(appointment)
        return appointment

    def get_by_id(
        self,
        appointment_id: uuid.UUID,
    ) -> Appointment | None:
        stmt: Select = select(Appointment).where(
            Appointment.id == appointment_id
        )

        return self.db.scalar(stmt)

    def get_by_patient(
        self,
        patient_id: uuid.UUID,
    ) -> list[Appointment]:
        stmt: Select = (
            select(Appointment)
            .where(Appointment.patient_id == patient_id)
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.start_time.desc(),
            )
        )

        return list(self.db.scalars(stmt).all())

    def get_by_doctor(
        self,
        doctor_id: uuid.UUID,
    ) -> list[Appointment]:
        stmt: Select = (
            select(Appointment)
            .where(Appointment.doctor_id == doctor_id)
            .order_by(
                Appointment.appointment_date.asc(),
                Appointment.start_time.asc(),
            )
        )

        return list(self.db.scalars(stmt).all())

    def get_by_doctor_date(
        self,
        doctor_id: uuid.UUID,
        appointment_date: date,
    ) -> list[Appointment]:
        stmt: Select = (
            select(Appointment)
            .where(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == appointment_date,
            )
            .order_by(Appointment.start_time.asc())
        )

        return list(self.db.scalars(stmt).all())

    def get_by_doctor_date_time(
        self,
        doctor_id: uuid.UUID,
        appointment_date: date,
        start_time: time,
    ) -> Appointment | None:
        stmt: Select = select(Appointment).where(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.start_time == start_time,
        )

        return self.db.scalar(stmt)

    def search(
        self,
        *,
        doctor_id: uuid.UUID | None = None,
        patient_id: uuid.UUID | None = None,
        department_id: uuid.UUID | None = None,
        appointment_date: date | None = None,
        status: str | None = None,
    ) -> list[Appointment]:
        stmt: Select = select(Appointment)

        if doctor_id:
            stmt = stmt.where(Appointment.doctor_id == doctor_id)

        if patient_id:
            stmt = stmt.where(Appointment.patient_id == patient_id)

        if department_id:
            stmt = stmt.where(
                Appointment.department_id == department_id
            )

        if appointment_date:
            stmt = stmt.where(
                Appointment.appointment_date == appointment_date
            )

        if status:
            stmt = stmt.where(Appointment.status == status)

        stmt = stmt.order_by(
            Appointment.appointment_date.asc(),
            Appointment.start_time.asc(),
        )

        return list(self.db.scalars(stmt).all())

    def update(
        self,
        appointment: Appointment,
    ) -> Appointment:
        self.db.flush()
        self.db.refresh(appointment)
        return appointment

    def exists(
        self,
        appointment_id: uuid.UUID,
    ) -> bool:
        stmt: Select = select(Appointment.id).where(
            Appointment.id == appointment_id
        )

        return self.db.scalar(stmt) is not None

    def delete(
        self,
        appointment: Appointment,
    ) -> None:
        self.db.delete(appointment)
        self.db.flush()