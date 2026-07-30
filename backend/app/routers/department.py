import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.department_repository import DepartmentRepository
from app.schemas.department import (DepartmentCreateRequest,
                                    DepartmentResponse,
                                    DepartmentUpdateRequest)
from app.services.department_service import DepartmentService

router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


def get_department_service(
    db: Session = Depends(get_db),
) -> DepartmentService:
    repository = DepartmentRepository(db)
    return DepartmentService(repository)


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_department(
    request: DepartmentCreateRequest,
    service: DepartmentService = Depends(get_department_service),
):
    return service.create_department(request)


@router.get(
    "",
    response_model=list[DepartmentResponse],
)
def list_departments(
    service: DepartmentService = Depends(get_department_service),
):
    return service.list_departments()


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def get_department(
    department_id: uuid.UUID,
    service: DepartmentService = Depends(get_department_service),
):
    return service.get_department(department_id)


@router.patch(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def update_department(
    department_id: uuid.UUID,
    request: DepartmentUpdateRequest,
    service: DepartmentService = Depends(get_department_service),
):
    return service.update_department(
        department_id,
        request,
    )


@router.delete(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def delete_department(
    department_id: uuid.UUID,
    service: DepartmentService = Depends(get_department_service),
):
    return service.delete_department(department_id)
