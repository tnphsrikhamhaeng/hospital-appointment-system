from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.doctor_schedule_template import (
    DoctorScheduleTemplateCreateRequest,
    DoctorScheduleTemplateResponse,
    DoctorScheduleTemplateUpdateRequest,
)
from app.services.doctor_schedule_template_service import (
    DoctorScheduleTemplateService,
)

router = APIRouter(
    prefix="/doctor-schedule-templates",
    tags=["Doctor Schedule Template"],
)


@router.post(
    "",
    response_model=DoctorScheduleTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_doctor_schedule_template(
    request: DoctorScheduleTemplateCreateRequest,
    db: Session = Depends(get_db),
) -> DoctorScheduleTemplateResponse:
    service = DoctorScheduleTemplateService(db)

    return service.create_template(request)


@router.get(
    "/{template_id}",
    response_model=DoctorScheduleTemplateResponse,
)
def get_doctor_schedule_template(
    template_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> DoctorScheduleTemplateResponse:
    service = DoctorScheduleTemplateService(db)

    return service.get_template(template_id)


@router.get(
    "/doctor/{doctor_id}",
    response_model=list[DoctorScheduleTemplateResponse],
)
def list_doctor_schedule_templates(
    doctor_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[DoctorScheduleTemplateResponse]:
    service = DoctorScheduleTemplateService(db)

    return service.list_by_doctor(doctor_id)


@router.patch(
    "/{template_id}",
    response_model=DoctorScheduleTemplateResponse,
)
def update_doctor_schedule_template(
    template_id: uuid.UUID,
    request: DoctorScheduleTemplateUpdateRequest,
    db: Session = Depends(get_db),
) -> DoctorScheduleTemplateResponse:
    service = DoctorScheduleTemplateService(db)

    return service.update_template(
        template_id=template_id,
        request=request,
    )


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_doctor_schedule_template(
    template_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Response:
    service = DoctorScheduleTemplateService(db)

    service.delete_template(template_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)