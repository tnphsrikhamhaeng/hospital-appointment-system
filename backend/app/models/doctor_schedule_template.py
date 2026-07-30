from __future__ import annotations

import uuid
from datetime import datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Time, func, true
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import WeekdayEnum

if TYPE_CHECKING:
    from app.models.doctor import Doctor


class DoctorScheduleTemplate(Base):
    __tablename__ = "doctor_schedule_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "doctors.id",
            name="fk_doctor_schedule_templates_doctor_id",
        ),
        nullable=False,
    )

    weekday: Mapped[WeekdayEnum] = mapped_column(
        Enum(
            WeekdayEnum,
            values_callable=lambda enum: [e.value for e in enum],
            name="weekdayenum",
        ),
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

    is_active: Mapped[bool] = mapped_column(
      Boolean,
      nullable=False,
      default=True,
      server_default=true(),
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

    doctor: Mapped["Doctor"] = relationship(
        "Doctor",
        back_populates="doctor_schedule_templates",
    )