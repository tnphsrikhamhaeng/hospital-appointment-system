from __future__ import annotations

import uuid
from datetime import date, datetime, time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.doctor import Doctor
    from app.models.department import Department
    from app.models.medical_record import MedicalRecord

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Time,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import AppointmentStatusEnum


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_appointments_patient_id",
        ),
        nullable=False,
    )

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "doctors.id",
            name="fk_appointments_doctor_id",
        ),
        nullable=False,
    )

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "departments.id",
            name="fk_appointments_department_id",
        ),
        nullable=False,
    )

    appointment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    status: Mapped[AppointmentStatusEnum] = mapped_column(
        Enum(
            AppointmentStatusEnum,
            values_callable=lambda enum: [e.value for e in enum],
            name="appointmentstatusenum",
        ),
        default=AppointmentStatusEnum.PENDING,
        nullable=False,
    )

    cancelled_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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

    patient: Mapped["User"] = relationship(
        "User",
    )

    doctor: Mapped["Doctor"] = relationship(
        "Doctor",
        back_populates="appointments",
    )

    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="appointments",
    )

    qr_code = relationship(
        "AppointmentQRCode",
        back_populates="appointment",
        uselist=False,
        cascade="all, delete-orphan",
    )

    medical_record: Mapped["MedicalRecord | None"] = relationship(
        "MedicalRecord",
        back_populates="appointment",
        uselist=False,
    )