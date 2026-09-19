from __future__ import annotations

import uuid
from datetime import time

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.enums import WeekdayEnum
from app.models.doctor_schedule_template import DoctorScheduleTemplate


class DoctorScheduleTemplateRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        doctor_schedule_template: DoctorScheduleTemplate,
    ) -> DoctorScheduleTemplate:
        self.db.add(doctor_schedule_template)
        self.db.flush()
        self.db.refresh(doctor_schedule_template)

        return doctor_schedule_template

    def update(
        self,
        doctor_schedule_template: DoctorScheduleTemplate,
    ) -> DoctorScheduleTemplate:
        self.db.flush()
        self.db.refresh(doctor_schedule_template)

        return doctor_schedule_template

    def delete(
        self,
        doctor_schedule_template: DoctorScheduleTemplate,
    ) -> None:
        self.db.delete(doctor_schedule_template)
        self.db.flush()

    def get_by_id(
        self,
        doctor_schedule_template_id: uuid.UUID,
    ) -> DoctorScheduleTemplate | None:
        statement = select(DoctorScheduleTemplate).where(
            DoctorScheduleTemplate.id == doctor_schedule_template_id,
        )

        return self.db.scalar(statement)

    def list_by_doctor(
        self,
        doctor_id: uuid.UUID,
    ) -> list[DoctorScheduleTemplate]:
        statement = (
            select(DoctorScheduleTemplate)
            .where(
                DoctorScheduleTemplate.doctor_id == doctor_id,
            )
            .order_by(
                DoctorScheduleTemplate.weekday,
                DoctorScheduleTemplate.start_time,
            )
        )

        return list(self.db.scalars(statement).all())

    def list_active_by_doctor(
        self,
        doctor_id: uuid.UUID,
    ) -> list[DoctorScheduleTemplate]:
        statement = (
            select(DoctorScheduleTemplate)
            .where(
                DoctorScheduleTemplate.doctor_id == doctor_id,
                DoctorScheduleTemplate.is_active.is_(True),
            )
            .order_by(
                DoctorScheduleTemplate.weekday,
                DoctorScheduleTemplate.start_time,
            )
        )

        return list(self.db.scalars(statement).all())

    def exists_overlapping_template(
        self,
        doctor_id: uuid.UUID,
        weekday: WeekdayEnum,
        start_time: time,
        end_time: time,
        exclude_template_id: uuid.UUID | None = None,
    ) -> bool:
        conditions = [
            DoctorScheduleTemplate.doctor_id == doctor_id,
            DoctorScheduleTemplate.weekday == weekday,
            DoctorScheduleTemplate.start_time < end_time,
            DoctorScheduleTemplate.end_time > start_time,
        ]

        if exclude_template_id is not None:
            conditions.append(
                DoctorScheduleTemplate.id != exclude_template_id,
            )

        statement = select(DoctorScheduleTemplate.id).where(
            and_(*conditions),
        )

        return self.db.scalar(statement) is not None
    
    def get_active_schedule(
        self,
        doctor_id: uuid.UUID,
        weekday: WeekdayEnum,
        start_time: time,
    ) -> DoctorScheduleTemplate | None:

        statement = (
            select(DoctorScheduleTemplate)
            .where(
                DoctorScheduleTemplate.doctor_id == doctor_id,
                DoctorScheduleTemplate.weekday == weekday,
                DoctorScheduleTemplate.is_active.is_(True),
                DoctorScheduleTemplate.start_time <= start_time,
                DoctorScheduleTemplate.end_time > start_time,
            )
        )

        return self.db.scalar(statement)