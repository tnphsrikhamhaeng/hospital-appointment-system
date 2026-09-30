from __future__ import annotations

import uuid
from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import Select, and_, select
from sqlalchemy.orm import Session, joinedload

from app.models.appointment import Appointment

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.doctor import Doctor
    from app.models.department import Department
    from app.models.medical_record import MedicalRecord


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
        previous_date = appointment_date - timedelta(days=1)

        stmt: Select = (
            select(Appointment)
            .options(
                joinedload(Appointment.patient),
            )
            .where(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date.in_(
                    [previous_date, appointment_date]
                ),
            )
            .order_by(
                Appointment.appointment_date.asc(),
                Appointment.start_time.asc(),
            )
        )

        appointments = list(self.db.scalars(stmt).all())

        result: list[Appointment] = []

        for appointment in appointments:
            # นัดหมายปกติของวันที่เลือก
            if appointment.appointment_date == appointment_date:
                result.append(appointment)
                continue

            # นัดหมายของวันก่อนหน้าที่ข้ามมาในวันปัจจุบัน
            if (
                appointment.end_time <= appointment.start_time
                and appointment_date == previous_date + timedelta(days=1)
            ):
                result.append(appointment)

        return result

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
        date_from: date | None = None,
        date_to: date | None = None,
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

        if date_from:
            stmt = stmt.where(
                Appointment.appointment_date >= date_from
            )

        if date_to:
            stmt = stmt.where(
                Appointment.appointment_date <= date_to
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

    def exists_overlapping_appointment(
        self,
        doctor_id: uuid.UUID,
        appointment_date: date,
        start_time: time,
        end_time: time,
        exclude_appointment_id: uuid.UUID | None = None,
    ) -> bool:
        conditions = [
            Appointment.doctor_id == doctor_id,
            Appointment.status != "cancelled",
        ]

        if exclude_appointment_id is not None:
            conditions.append(
                Appointment.id != exclude_appointment_id
            )

        appointments = self.db.scalars(
            select(Appointment).where(
                and_(*conditions)
            )
        ).all()

        new_start = datetime.combine(
            appointment_date,
            start_time,
        )

        new_end = datetime.combine(
            appointment_date,
            end_time,
        )

        if end_time <= start_time:
            new_end = new_end.replace(
                day=new_end.day
            )
            new_end = new_end.replace(
                hour=end_time.hour,
                minute=end_time.minute,
                second=end_time.second,
                microsecond=end_time.microsecond,
            )

            from datetime import timedelta
            new_end += timedelta(days=1)

        for appointment in appointments:
            existing_start = datetime.combine(
                appointment.appointment_date,
                appointment.start_time,
            )

            existing_end = datetime.combine(
                appointment.appointment_date,
                appointment.end_time,
            )

            if appointment.end_time <= appointment.start_time:
                from datetime import timedelta
                existing_end += timedelta(days=1)

            if existing_start < new_end and existing_end > new_start:
                return True

        return False

    def exists_overlapping_patient_appointment(
        self,
        patient_id: uuid.UUID,
        appointment_date: date,
        start_time: time,
        end_time: time,
        exclude_appointment_id: uuid.UUID | None = None,
    ) -> bool:
        conditions = [
            Appointment.patient_id == patient_id,
            Appointment.status != "cancelled",
        ]

        if exclude_appointment_id is not None:
            conditions.append(
                Appointment.id != exclude_appointment_id
            )

        appointments = self.db.scalars(
            select(Appointment).where(
                and_(*conditions)
            )
        ).all()

        new_start = datetime.combine(
            appointment_date,
            start_time,
        )

        new_end = datetime.combine(
            appointment_date,
            end_time,
        )

        if end_time <= start_time:
            new_end += timedelta(days=1)

        for appointment in appointments:
            existing_start = datetime.combine(
                appointment.appointment_date,
                appointment.start_time,
            )

            existing_end = datetime.combine(
                appointment.appointment_date,
                appointment.end_time,
            )

            if appointment.end_time <= appointment.start_time:
                existing_end += timedelta(days=1)

            if existing_start < new_end and existing_end > new_start:
                return True

        return False

    def get_confirmed_appointments_between(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> list[Appointment]:
        statement = (
            select(Appointment)
            .where(
                Appointment.status == "confirmed",
                Appointment.appointment_date >= start_datetime.date(),
                Appointment.appointment_date <= end_datetime.date(),
            )
            .order_by(
                Appointment.appointment_date.asc(),
                Appointment.start_time.asc(),
            )
        )

        appointments = list(
            self.db.scalars(statement).all()
        )

        result: list[Appointment] = []

        for appointment in appointments:
            appointment_datetime = datetime.combine(
                appointment.appointment_date,
                appointment.start_time,
                tzinfo=start_datetime.tzinfo,
            )

            if start_datetime <= appointment_datetime < end_datetime:
                result.append(appointment)

        return result