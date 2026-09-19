from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.password_reset import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    StaffForgotPasswordRequest,
)
from app.services.password_reset_service import PasswordResetService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/forgot-password",
)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> dict:
    password_reset_service = PasswordResetService(db)

    reset_token = password_reset_service.request_reset(
        request,
    )

    return {
        "message": "Password reset token generated",
        "reset_token": reset_token,
    }
    
@router.post(
    "/staff-forgot-password",
)
def staff_forgot_password(
    request: StaffForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> dict:
    password_reset_service = PasswordResetService(db)

    reset_token = password_reset_service.request_staff_reset(
        request,
    )

    return {
        "message": "Password reset token generated",
        "reset_token": reset_token,
    }


@router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> None:
    password_reset_service = PasswordResetService(db)

    password_reset_service.reset_password(
        request,
    )