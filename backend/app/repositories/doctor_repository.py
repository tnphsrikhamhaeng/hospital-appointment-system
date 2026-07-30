from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import (Session,
    selectinload
)

from app.models.doctor import Doctor
from app.core.enums import DoctorStatusEnum


class DoctorRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, doctor: Doctor) -> Doctor:
        self.db.add(doctor)
        self.db.commit()
        self.db.refresh(doctor)
        return doctor

    def get_by_id(
        self,
        doctor_id: uuid.UUID,
        status: DoctorStatusEnum | None = None,
    ) -> Doctor | None:
        stmt = (
            select(Doctor)
            .where(Doctor.id == doctor_id)
            .options(
                selectinload(Doctor.department),
                selectinload(Doctor.specializations),
            )
        )

        if status is not None:
            stmt = stmt.where(Doctor.status == status)

        return self.db.scalar(stmt)

    def get_by_email(self, email: str) -> Doctor | None:
        stmt = select(Doctor).where(Doctor.email == email)
        return self.db.scalar(stmt)

    def get_by_phone_number(self, phone_number: str) -> Doctor | None:
        stmt = select(Doctor).where(Doctor.phone_number == phone_number)
        return self.db.scalar(stmt)

    def get_by_license_number(
        self,
        license_number: str,
    ) -> Doctor | None:
        stmt = select(Doctor).where(Doctor.license_number == license_number)
        return self.db.scalar(stmt)

    def update(self, doctor: Doctor) -> Doctor:
        self.db.commit()
        self.db.refresh(doctor)
        return doctor

    def delete(self, doctor: Doctor) -> None:
        self.db.delete(doctor)
        self.db.commit()

    def get_doctors(
        self,
        status: DoctorStatusEnum | None = None,
    ) -> list[Doctor]:
        stmt = (
            select(Doctor)
            .options(
                selectinload(Doctor.department),
                selectinload(Doctor.specializations),
            )
            .order_by(Doctor.created_at.desc())
        )

        if status is not None:
            stmt = stmt.where(Doctor.status == status)

        return list(self.db.scalars(stmt).all())