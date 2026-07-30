from __future__ import annotations
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.doctor import DoctorCreateRequest, DoctorResponse, DoctorUpdateRequest
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
) -> DoctorResponse:
    return service.create_doctor(request)

@router.get(
    "",
    response_model=list[DoctorResponse],
    status_code=status.HTTP_200_OK,
)
def get_doctors(
    service: DoctorService = Depends(get_doctor_service),
):
    return service.get_doctors()

@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse,
    status_code=status.HTTP_200_OK,
)
def get_doctor_by_id(
    doctor_id: uuid.UUID,
    service: DoctorService = Depends(get_doctor_service),
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
    service: DoctorService = Depends(get_doctor_service),
):
    return service.delete_doctor(doctor_id)