from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import DepartmentStatusEnum
from app.models.department import Department


class DepartmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, department_id: uuid.UUID) -> Department | None:
        stmt = select(Department).where(Department.id == department_id)
        return self.db.scalar(stmt)

    def get_by_name(self, name: str) -> Department | None:
        stmt = select(Department).where(
            Department.name == name,
            Department.status == DepartmentStatusEnum.ACTIVE,
        )
        return self.db.scalar(stmt)

    def get_all(self) -> list[Department]:
        stmt = (
            select(Department)
            .where(Department.status == DepartmentStatusEnum.ACTIVE)
            .order_by(Department.name)
        )
        return list(self.db.scalars(stmt).all())

    def create(self, department: Department) -> Department:
        self.db.add(department)
        self.db.commit()
        self.db.refresh(department)
        return department

    def update(self, department: Department) -> Department:
        self.db.commit()
        self.db.refresh(department)
        return department
