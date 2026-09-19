from __future__ import annotations
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.core.enums import UserRoleEnum, UserStatusEnum
from app.models.user import User
from app.schemas.staff import (
    StaffCreateRequest,
    StaffDeactivateRequest,
    StaffUpdateRequest,
)
from app.schemas.user import UserResponse
from app.services.staff_service import StaffService


router = APIRouter(prefix="/staff", tags=["Staff"])


def get_staff_service(db: Session = Depends(get_db)) -> StaffService:
    return StaffService(db)


@router.get(
    "",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
def list_staff(
    status_filter: UserStatusEnum | None = Query(
        default=None,
        alias="status",
    ),
    search: str | None = Query(default=None),
    service: StaffService = Depends(get_staff_service),
    current_user: User = Depends(
        require_roles(UserRoleEnum.HOSPITAL_STAFF),
    ),
) -> list[UserResponse]:
    return service.list_staff(
        status=status_filter,
        search=search,
    )

@router.patch(
    "/{staff_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def update_staff(
    staff_id: uuid.UUID,
    request: StaffUpdateRequest,
    service: StaffService = Depends(get_staff_service),
    current_user: User = Depends(
        require_roles(UserRoleEnum.HOSPITAL_STAFF),
    ),
) -> UserResponse:
    return service.update_staff(
        staff_id,
        request,
    )

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_staff(
    request: StaffCreateRequest,
    service: StaffService = Depends(get_staff_service),
    current_user: User = Depends(
        require_roles(UserRoleEnum.HOSPITAL_STAFF),
    ),
) -> UserResponse:
    return service.create_staff(request)

@router.delete(
    "/{staff_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def deactivate_staff(
    staff_id: uuid.UUID,
    request: StaffDeactivateRequest,
    service: StaffService = Depends(get_staff_service),
    current_user: User = Depends(
        require_roles(UserRoleEnum.HOSPITAL_STAFF),
    ),
) -> UserResponse:
    return service.deactivate_staff(
        staff_id,
        request,
        current_user,
    )