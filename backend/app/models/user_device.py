from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
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
from app.core.enums import DevicePlatformEnum


class UserDevice(Base):
    __tablename__ = "user_devices"

    __table_args__ = (
      UniqueConstraint(
          "device_token",
          name="uq_user_devices_device_token",
      ),
      Index(
          "ix_user_devices_user_active",
          "user_id",
          "is_active",
      ),
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_user_devices_user_id",
        ),
        nullable=False,
    )

    device_token: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    platform: Mapped[DevicePlatformEnum] = mapped_column(
        Enum(
            DevicePlatformEnum,
            values_callable=lambda enum: [e.value for e in enum],
            name="deviceplatformenum",
        ),
        nullable=False,
    )

    device_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    last_used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
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

    user: Mapped["User"] = relationship(
        "User",
        back_populates="devices",
    )