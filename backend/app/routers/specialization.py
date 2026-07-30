import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.department_repository import DepartmentRepository
from app.repositories.specialization_repository import SpecializationRepository
from app.schemas.specialization import (SpecializationCreateRequest,
                                        SpecializationResponse,
                                        SpecializationUpdateRequest)
from app.services.specialization_service import SpecializationService

router = APIRouter(
    prefix="/specializations",
    tags=["Specializations"],
)


def get_specialization_service(
    db: Session = Depends(get_db),
) -> SpecializationService:
    specialization_repository = SpecializationRepository(db)
    department_repository = DepartmentRepository(db)

    return SpecializationService(
        specialization_repository=specialization_repository,
        department_repository=department_repository,
    )


@router.post(
    "",
    response_model=SpecializationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_specialization(
    request: SpecializationCreateRequest,
    service: SpecializationService = Depends(get_specialization_service),
):
    return service.create_specialization(request)


@router.get(
    "",
    response_model=list[SpecializationResponse],
)
def list_specializations(
    service: SpecializationService = Depends(get_specialization_service),
):
    return service.list_specializations()


@router.get(
    "/{specialization_id}",
    response_model=SpecializationResponse,
)
def get_specialization(
    specialization_id: uuid.UUID,
    service: SpecializationService = Depends(get_specialization_service),
):
    return service.get_specialization(specialization_id)


@router.patch(
    "/{specialization_id}",
    response_model=SpecializationResponse,
)
def update_specialization(
    specialization_id: uuid.UUID,
    request: SpecializationUpdateRequest,
    service: SpecializationService = Depends(get_specialization_service),
):
    return service.update_specialization(
        specialization_id,
        request,
    )


@router.delete(
    "/{specialization_id}",
    response_model=SpecializationResponse,
)
def delete_specialization(
    specialization_id: uuid.UUID,
    service: SpecializationService = Depends(get_specialization_service),
):
    return service.delete_specialization(specialization_id)
