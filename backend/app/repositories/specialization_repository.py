from __future__ import annotations

import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.enums import SpecializationStatusEnum
from app.models.specialization import Specialization


class SpecializationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_ids(
        self,
        specialization_ids: list[uuid.UUID],
    ) -> list[Specialization]:
        stmt = select(Specialization).where(
            Specialization.id.in_(specialization_ids)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(
        self,
        specialization_id: uuid.UUID,
    ) -> Specialization | None:
        stmt = select(Specialization).where(
            Specialization.id == specialization_id
        )
        return self.db.scalar(stmt)

    def get_by_name(
        self,
        name: str,
    ) -> Specialization | None:
        stmt = select(Specialization).where(
            Specialization.name == name
        )
        return self.db.scalar(stmt)

    def get_by_department_and_name(
        self,
        department_id: uuid.UUID,
        name: str,
    ) -> Specialization | None:
        stmt = select(Specialization).where(
            Specialization.department_id == department_id,
            Specialization.name == name,
        )
        return self.db.scalar(stmt)

    def get_all(
        self,
    ) -> list[Specialization]:
        stmt = (
            select(Specialization)
            .where(
                Specialization.status
                == SpecializationStatusEnum.ACTIVE
            )
            .order_by(Specialization.name)
        )
        return list(self.db.scalars(stmt).all())

    def get_specializations(
        self,
        status: SpecializationStatusEnum | None = None,
        search: str | None = None,
    ) -> list[Specialization]:
        stmt = (
            select(Specialization)
            .order_by(Specialization.name)
        )

        if status is not None:
            stmt = stmt.where(
                Specialization.status == status
            )

        if search:
            search_value = f"%{search.strip()}%"

            stmt = stmt.where(
                or_(
                    Specialization.name.ilike(search_value),
                    Specialization.description.ilike(search_value),
                )
            )

        return list(self.db.scalars(stmt).all())

    def create(
        self,
        specialization: Specialization,
    ) -> Specialization:
        self.db.add(specialization)
        self.db.commit()
        self.db.refresh(specialization)
        return specialization

    def update(
        self,
        specialization: Specialization,
    ) -> Specialization:
        self.db.commit()
        self.db.refresh(specialization)
        return specialization