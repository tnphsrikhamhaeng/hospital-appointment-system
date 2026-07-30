from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.doctor import Doctor
    from app.models.specialization import Specialization
    from app.models.appointment import Appointment

from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text, func,Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import DepartmentStatusEnum
from app.core.database import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    slot_duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
    )
        
    status: Mapped[DepartmentStatusEnum] = mapped_column(
        Enum(
            DepartmentStatusEnum,
            values_callable=lambda enum: [e.value for e in enum],
            name="DepartmentStatusEnum",
        ),
        default=DepartmentStatusEnum.ACTIVE,
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

    doctors: Mapped[list["Doctor"]] = relationship(
        "Doctor",
        back_populates="department",
    )

    specializations: Mapped[list["Specialization"]] = relationship(
        "Specialization",
        back_populates="department",
    )

    appointments: Mapped[list["Appointment"]] = relationship(
    "Appointment",
    back_populates="department",
    )