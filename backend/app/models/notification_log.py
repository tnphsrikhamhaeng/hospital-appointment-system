from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.user import User

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    func,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.database import Base
from app.core.enums import (
    NotificationStatusEnum,
    NotificationTypeEnum,
)


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    __table_args__ = (
        Index(
            "ix_notification_logs_appointment_id",
            "appointment_id",
        ),
        Index(
            "ix_notification_logs_patient_id",
            "patient_id",
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
            name="fk_notification_logs_appointment_id",
        ),
        nullable=False,
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_notification_logs_patient_id",
        ),
        nullable=False,
    )

    notification_type: Mapped[NotificationTypeEnum] = mapped_column(
        Enum(
            NotificationTypeEnum,
            values_callable=lambda enum: [e.value for e in enum],
            name="notificationtypeenum",
        ),
        nullable=False,
    )

    notification_status: Mapped[
        NotificationStatusEnum
    ] = mapped_column(
        Enum(
            NotificationStatusEnum,
            values_callable=lambda enum: [e.value for e in enum],
            name="notificationstatusenum",
        ),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    body: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    appointment: Mapped["Appointment"] = relationship(
        "Appointment",
    )

    patient: Mapped["User"] = relationship(
        "User",
    )