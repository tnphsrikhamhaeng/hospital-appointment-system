from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user_device_schema import (
    UserDeviceRegisterRequest,
    UserDeviceResponse,
)
from app.services.user_device_service import UserDeviceService


router = APIRouter(
    prefix="/user-devices",
    tags=["User Devices"],
)


@router.post(
    "",
    response_model=UserDeviceResponse,
    status_code=status.HTTP_200_OK,
)
def register_or_update_device(
    request: UserDeviceRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserDeviceResponse:
    user_device_service = UserDeviceService(db)

    return user_device_service.register_or_update_device(
        user_id=current_user.id,
        request=request,
    )