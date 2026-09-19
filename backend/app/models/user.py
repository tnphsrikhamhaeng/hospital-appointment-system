import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.doctor import Doctor
    from app.models.user_device import UserDevice
    from app.models.medical_record import MedicalRecord

from app.core.database import Base
from app.core.enums import GenderEnum, UserRoleEnum, UserStatusEnum


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    username: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    password: Mapped[str] = mapped_column(
        String(255),
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
        unique=True,
        nullable=False,
    )

    gender: Mapped[GenderEnum | None] = mapped_column(
        Enum(GenderEnum, name="gender_enum"),
        nullable=True,
    )

    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    role: Mapped[UserRoleEnum] = mapped_column(
        Enum(UserRoleEnum, name="user_role_enum"),
        nullable=False,
        default=UserRoleEnum.PATIENT,
    )

    status: Mapped[UserStatusEnum] = mapped_column(
        Enum(UserStatusEnum, name="user_status_enum"),
        nullable=False,
        default=UserStatusEnum.ACTIVE,
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
    
    doctor: Mapped["Doctor | None"] = relationship(
        "Doctor",
        back_populates="user",
        uselist=False,
    )
    
    appointments: Mapped[list["Appointment"]] = relationship(
    "Appointment",
    back_populates="patient",
    )
    
    devices: Mapped[list["UserDevice"]] = relationship(
        "UserDevice",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    medical_records: Mapped[list["MedicalRecord"]] = relationship(
        "MedicalRecord",
        back_populates="patient",
    )