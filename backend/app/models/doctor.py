from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import DoctorPrefaceEnum, DoctorStatusEnum

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.department import Department
    from app.models.doctor_schedule_template import DoctorScheduleTemplate
    from app.models.doctor_specialization import DoctorSpecialization
    from app.models.medical_record import MedicalRecord
    from app.models.specialization import Specialization
    from app.models.user import User


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_doctors_user_id",
        ),
        nullable=True,
        unique=True,
    )

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "departments.id",
            name="fk_doctors_department_id",
        ),
        nullable=False,
    )

    license_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    profile_image_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    preface: Mapped[DoctorPrefaceEnum] = mapped_column(
        Enum(
            DoctorPrefaceEnum,
            values_callable=lambda enum: [e.value for e in enum],
            name="doctorprefaceenum",
        ),
        nullable=False,
    )

    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    phone_number: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        unique=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    status: Mapped[DoctorStatusEnum] = mapped_column(
        Enum(
            DoctorStatusEnum,
            values_callable=lambda enum: [e.value for e in enum],
            name="DoctorStatusEnum",
        ),
        default=DoctorStatusEnum.ACTIVE,
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

    user: Mapped["User | None"] = relationship(
        "User",
        back_populates="doctor",
        uselist=False,
    )

    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="doctors",
    )

    doctor_specializations: Mapped[list["DoctorSpecialization"]] = relationship(
        "DoctorSpecialization",
        back_populates="doctor",
    )

    specializations: Mapped[list["Specialization"]] = relationship(
        "Specialization",
        secondary="doctor_specializations",
        viewonly=True,
    )

    doctor_schedule_templates: Mapped[list["DoctorScheduleTemplate"]] = relationship(
        "DoctorScheduleTemplate",
        back_populates="doctor",
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        back_populates="doctor",
    )

    medical_records: Mapped[list["MedicalRecord"]] = relationship(
        "MedicalRecord",
        back_populates="doctor",
    )