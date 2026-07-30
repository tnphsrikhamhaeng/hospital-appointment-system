from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.doctor_specialization import DoctorSpecialization

from datetime import datetime

from sqlalchemy import (DateTime, Enum, ForeignKey, String, Text,
                        UniqueConstraint, func)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import SpecializationStatusEnum
from app.core.database import Base

class Specialization(Base):
    __tablename__ = "specializations"

    __table_args__ = (
        UniqueConstraint(
            "department_id",
            "name",
            name="uq_specialization_department_name",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
        "departments.id",
        name="fk_specializations_department_id",
    ),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[SpecializationStatusEnum] = mapped_column(
        Enum(
            SpecializationStatusEnum,
            values_callable=lambda enum: [e.value for e in enum],
            name="SpecializationStatusEnum",
        ),
        default=SpecializationStatusEnum.ACTIVE,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="specializations",
    )

    doctor_specializations: Mapped[list["DoctorSpecialization"]] = relationship(
        "DoctorSpecialization",
        back_populates="specialization",
    )
