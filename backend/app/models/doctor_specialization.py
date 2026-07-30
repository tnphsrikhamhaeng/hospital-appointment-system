from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.doctor import Doctor
    from app.models.specialization import Specialization


class DoctorSpecialization(Base):
    __tablename__ = "doctor_specializations"

    __table_args__ = (
        UniqueConstraint(
            "doctor_id",
            "specialization_id",
            name="uq_doctor_specialization",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "doctors.id",
            name="fk_doctor_specializations_doctor_id",
        ),
        nullable=False,
    )

    specialization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "specializations.id",
            name="fk_doctor_specializations_specialization_id",
        ),
        nullable=False,
    )

    doctor: Mapped["Doctor"] = relationship(
        "Doctor",
        back_populates="doctor_specializations",
    )

    specialization: Mapped["Specialization"] = relationship(
        "Specialization",
        back_populates="doctor_specializations",
    )