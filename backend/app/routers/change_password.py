from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.change_password import ChangePasswordRequest
from app.services.change_password_service import ChangePasswordService


router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)


@router.patch(
    "/password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    change_password_service = ChangePasswordService(db)

    change_password_service.change_password(
        current_user=current_user,
        request=request,
    )