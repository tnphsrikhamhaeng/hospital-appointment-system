import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.core.enums import SpecializationStatusEnum, UserRoleEnum
from app.models.user import User
from app.repositories.department_repository import DepartmentRepository
from app.repositories.specialization_repository import SpecializationRepository
from app.schemas.specialization import (
    SpecializationCreateRequest,
    SpecializationResponse,
    SpecializationUpdateRequest,
)
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
    current_user: User = Depends(
        require_roles(UserRoleEnum.HOSPITAL_STAFF),
    ),
):
    return service.create(request)


@router.get(
    "",
    response_model=list[SpecializationResponse],
)
def list_specializations(
    status_filter: SpecializationStatusEnum | None = Query(
        default=None,
        alias="status",
    ),
    search: str | None = Query(
        default=None,
    ),
    service: SpecializationService = Depends(get_specialization_service),
    current_user: User = Depends(get_current_user),
):
    return service.list(
        status=status_filter,
        search=search,
    )


@router.get(
    "/{specialization_id}",
    response_model=SpecializationResponse,
)
def get_specialization(
    specialization_id: uuid.UUID,
    service: SpecializationService = Depends(get_specialization_service),
    current_user: User = Depends(get_current_user),
):
    return service.get(specialization_id)


@router.patch(
    "/{specialization_id}",
    response_model=SpecializationResponse,
)
def update_specialization(
    specialization_id: uuid.UUID,
    request: SpecializationUpdateRequest,
    service: SpecializationService = Depends(get_specialization_service),
    current_user: User = Depends(
        require_roles(UserRoleEnum.HOSPITAL_STAFF),
    ),
):
    return service.update(
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
    current_user: User = Depends(
        require_roles(UserRoleEnum.HOSPITAL_STAFF),
    ),
):
    return service.delete(specialization_id)