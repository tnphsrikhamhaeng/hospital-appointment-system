from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.core.enums import DepartmentStatusEnum, UserRoleEnum
from app.models.user import User
from app.repositories.department_repository import DepartmentRepository
from app.schemas.department import (
    DepartmentCreateRequest,
    DepartmentDeactivateRequest,
    DepartmentResponse,
    DepartmentUpdateRequest,
)
from app.services.department_service import DepartmentService


router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


def get_department_service(
    db: Session = Depends(get_db),
) -> DepartmentService:
    repository = DepartmentRepository(db)

    return DepartmentService(
        repository,
        db,
    )


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_department(
    request: DepartmentCreateRequest,
    service: DepartmentService = Depends(get_department_service),
    current_user: User = Depends(
        require_roles(UserRoleEnum.HOSPITAL_STAFF),
    ),
):
    return service.create(request)


@router.get(
    "",
    response_model=list[DepartmentResponse],
    status_code=status.HTTP_200_OK,
)
def list_departments(
    status_filter: DepartmentStatusEnum | None = Query(
        default=None,
        alias="status",
    ),
    search: str | None = Query(
        default=None,
    ),
    service: DepartmentService = Depends(get_department_service),
):
    return service.list(
        status=status_filter,
        search=search,
    )


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
)
def get_department(
    department_id: uuid.UUID,
    service: DepartmentService = Depends(get_department_service),
):
    return service.get(department_id)


@router.patch(
    "/{department_id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
)
def update_department(
    department_id: uuid.UUID,
    request: DepartmentUpdateRequest,
    service: DepartmentService = Depends(get_department_service),
    current_user: User = Depends(
        require_roles(UserRoleEnum.HOSPITAL_STAFF),
    ),
):
    return service.update(
        department_id,
        request,
    )


@router.delete(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def delete_department(
    department_id: uuid.UUID,
    request: DepartmentDeactivateRequest,
    service: DepartmentService = Depends(get_department_service),
    current_user: User = Depends(
        require_roles(UserRoleEnum.HOSPITAL_STAFF),
    ),
):
    return service.delete(
        department_id,
        request,
        current_user,
    )