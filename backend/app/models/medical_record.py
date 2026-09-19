from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.user import User
    from app.models.doctor import Doctor

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
    func,
    Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    __table_args__ = (
      UniqueConstraint(
          "appointment_id",
          name="uq_medical_records_appointment_id",
      ),
      Index(
          "ix_medical_records_patient_id",
          "patient_id",
      ),
      Index(
          "ix_medical_records_doctor_id",
          "doctor_id",
      ),
      Index(
          "ix_medical_records_created_at",
          "created_at",
      ),
  )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    appointment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "appointments.id",
            name="fk_medical_records_appointment_id",
        ),
        nullable=False,
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_medical_records_patient_id",
        ),
        nullable=False,
    )

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "doctors.id",
            name="fk_medical_records_doctor_id",
        ),
        nullable=False,
    )

    chief_complaint: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    present_illness: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    physical_examination: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    diagnosis: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    treatment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    recommendation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
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

    appointment: Mapped["Appointment"] = relationship(
        "Appointment",
        back_populates="medical_record",
        uselist=False,
    )

    patient: Mapped["User"] = relationship(
        "User",
        back_populates="medical_records",
    )

    doctor: Mapped["Doctor"] = relationship(
        "Doctor",
        back_populates="medical_records",
    )