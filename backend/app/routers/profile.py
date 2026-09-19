from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import (
    ProfileResponse,
    UpdateProfileRequest,
)
from app.services.profile_service import ProfileService


router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)


@router.get(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    profile_service = ProfileService(db)

    return profile_service.get_profile(
        current_user=current_user,
    )


@router.patch(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
)
def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    profile_service = ProfileService(db)

    return profile_service.update_profile(
        current_user=current_user,
        request=request,
    )