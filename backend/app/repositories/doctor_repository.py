from __future__ import annotations

import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.enums import DoctorStatusEnum
from app.models.doctor import Doctor
from app.models.user import User


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
        stmt = select(Doctor).where(
            Doctor.license_number == license_number,
        )
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
        department_id: uuid.UUID | None = None,
        status: DoctorStatusEnum | None = None,
        search: str | None = None,
    ) -> list[Doctor]:
        stmt = (
            select(Doctor)
            .join(User, Doctor.user_id == User.id, isouter=True)
            .options(
                selectinload(Doctor.department),
                selectinload(Doctor.specializations),
            )
            .order_by(Doctor.created_at.desc())
        )

        if department_id is not None:
            stmt = stmt.where(
                Doctor.department_id == department_id,
            )

        if status is not None:
            stmt = stmt.where(
                Doctor.status == status,
            )

        if search:
            search_value = f"%{search.strip()}%"

            stmt = stmt.where(
                or_(
                    User.username.ilike(search_value),
                    Doctor.first_name.ilike(search_value),
                    Doctor.last_name.ilike(search_value),
                    Doctor.license_number.ilike(search_value),
                    Doctor.email.ilike(search_value),
                )
            )

        return list(self.db.scalars(stmt).unique().all())

    def get_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> Doctor | None:
        stmt = select(Doctor).where(
            Doctor.user_id == user_id,
        )
        return self.db.scalar(stmt)