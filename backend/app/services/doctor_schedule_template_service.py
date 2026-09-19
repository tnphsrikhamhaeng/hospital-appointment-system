from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.models.doctor import Doctor
from app.models.doctor_schedule_template import DoctorScheduleTemplate
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.doctor_schedule_template_repository import (
    DoctorScheduleTemplateRepository,
)
from app.schemas.doctor_schedule_template import (
    DoctorScheduleTemplateCreateRequest,
    DoctorScheduleTemplateResponse,
    DoctorScheduleTemplateUpdateRequest,
)

from app.core.enums import UserRoleEnum
from app.core.exceptions import (
    ConflictException,
    NotFoundException,
)
from app.models.user import User

class DoctorScheduleTemplateService:
    def __init__(self, db: Session):
        self.db = db
        self.doctor_repository = DoctorRepository(db)
        self.repository = DoctorScheduleTemplateRepository(db)

    def create_template(
        self,
        request: DoctorScheduleTemplateCreateRequest,
    ) -> DoctorScheduleTemplateResponse:
        doctor: Doctor | None = self.doctor_repository.get_by_id(
            request.doctor_id,
        )

        if doctor is None:
            raise NotFoundException("Doctor not found.")

        if self.repository.exists_overlapping_template(
            doctor_id=request.doctor_id,
            weekday=request.weekday,
            start_time=request.start_time,
            end_time=request.end_time,
        ):
            raise ConflictException(
                "Schedule template overlaps an existing template.",
            )

        template = DoctorScheduleTemplate(
            doctor_id=request.doctor_id,
            weekday=request.weekday,
            start_time=request.start_time,
            end_time=request.end_time,
        )

        template = self.repository.create(template)

        self.db.commit()

        return DoctorScheduleTemplateResponse.model_validate(template)

    def update_template(
        self,
        template_id: uuid.UUID,
        request: DoctorScheduleTemplateUpdateRequest,
    ) -> DoctorScheduleTemplateResponse:
        template = self.repository.get_by_id(template_id)

        if template is None:
            raise NotFoundException("Doctor schedule template not found.")

        weekday = request.weekday or template.weekday
        start_time = request.start_time or template.start_time
        end_time = request.end_time or template.end_time

        if self.repository.exists_overlapping_template(
            doctor_id=template.doctor_id,
            weekday=weekday,
            start_time=start_time,
            end_time=end_time,
            exclude_template_id=template.id,
        ):
            raise ConflictException(
                "Schedule template overlaps an existing template.",
            )

        update_data = request.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(template, field, value)

        template = self.repository.update(template)

        self.db.commit()

        return DoctorScheduleTemplateResponse.model_validate(template)

    def delete_template(
        self,
        template_id: uuid.UUID,
    ) -> None:
        template = self.repository.get_by_id(template_id)

        if template is None:
            raise NotFoundException("Doctor schedule template not found.")

        self.repository.delete(template)

        self.db.commit()

    def get_template(
        self,
        template_id: uuid.UUID,
    ) -> DoctorScheduleTemplateResponse:
        template = self.repository.get_by_id(template_id)

        if template is None:
            raise NotFoundException("Doctor schedule template not found.")

        return DoctorScheduleTemplateResponse.model_validate(template)

    def list_by_doctor(
        self,
        doctor_id: uuid.UUID,
    ) -> list[DoctorScheduleTemplateResponse]:
        doctor = self.doctor_repository.get_by_id(doctor_id)

        if doctor is None:
            raise NotFoundException("Doctor not found.")

        templates = self.repository.list_by_doctor(doctor_id)

        return [
            DoctorScheduleTemplateResponse.model_validate(template)
            for template in templates
        ]
        
    def get_my_schedule(
        self,
        current_user: User,
    ) -> list[DoctorScheduleTemplateResponse]:
        if current_user.role != UserRoleEnum.DOCTOR:
            raise ConflictException(
                "Only doctor can view their own schedule."
            )

        doctor = self.doctor_repository.get_by_user_id(
            current_user.id,
        )

        if doctor is None:
            raise NotFoundException(
                "Doctor profile not found."
            )

        return self.list_by_doctor(doctor.id)