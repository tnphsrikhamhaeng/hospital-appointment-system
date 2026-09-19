from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.core.enums import DoctorStatusEnum, UserRoleEnum
from app.models.user import User
from app.schemas.doctor import (
    DoctorCreateRequest,
    DoctorDeactivateRequest,
    DoctorResponse,
    DoctorUpdateRequest,
)
from app.services.doctor_service import DoctorService


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"],
)


def get_doctor_service(
    db: Session = Depends(get_db),
) -> DoctorService:
    return DoctorService(db)


@router.post(
    "",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_doctor(
    request: DoctorCreateRequest,
    service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(
        require_roles(UserRoleEnum.HOSPITAL_STAFF),
    ),
) -> DoctorResponse:
    return service.create_doctor(request)


@router.get(
    "",
    response_model=list[DoctorResponse],
    status_code=status.HTTP_200_OK,
)
def get_doctors(
    department_id: uuid.UUID | None = Query(
        default=None,
    ),
    doctor_status: DoctorStatusEnum | None = Query(
        default=None,
        alias="status",
    ),
    search: str | None = Query(
        default=None,
    ),
    service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(get_current_user),
):
    return service.get_doctors(
        department_id=department_id,
        status=doctor_status,
        search=search,
    )


@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse,
    status_code=status.HTTP_200_OK,
)
def get_doctor_by_id(
    doctor_id: uuid.UUID,
    service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(get_current_user),
):
    return service.get_doctor_by_id(doctor_id)


@router.patch(
    "/{doctor_id}",
    response_model=DoctorResponse,
    status_code=status.HTTP_200_OK,
)
def update_doctor(
    doctor_id: uuid.UUID,
    request: DoctorUpdateRequest,
    service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(
        require_roles(UserRoleEnum.HOSPITAL_STAFF),
    ),
):
    return service.update_doctor(
        doctor_id=doctor_id,
        request=request,
    )


@router.delete(
    "/{doctor_id}",
    response_model=DoctorResponse,
    status_code=status.HTTP_200_OK,
)
def delete_doctor(
    doctor_id: uuid.UUID,
    request: DoctorDeactivateRequest,
    service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(
        require_roles(UserRoleEnum.HOSPITAL_STAFF),
    ),
):
    return service.delete_doctor(
        doctor_id=doctor_id,
        request=request,
        current_user=current_user,
    )