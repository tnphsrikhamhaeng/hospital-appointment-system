from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.core.enums import UserRoleEnum
from app.models.user import User
from app.schemas.reactivate import ReactivateRequest
from app.services.reactivate_service import ReactivateService


router = APIRouter(
    prefix="/reactivate",
    tags=["Reactivate"],
)


def get_reactivate_service(
    db: Session = Depends(get_db),
) -> ReactivateService:
    return ReactivateService(db)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
)
def reactivate(
    request: ReactivateRequest,
    service: ReactivateService = Depends(
        get_reactivate_service,
    ),
    current_user: User = Depends(
        require_roles(UserRoleEnum.HOSPITAL_STAFF),
    ),
):
    return service.reactivate(
        request=request,
        current_user=current_user,
    )