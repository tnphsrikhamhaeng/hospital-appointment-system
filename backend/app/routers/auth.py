from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
) -> RegisterResponse:
    auth_service = AuthService(db)

    return auth_service.register(request)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    service = AuthService(db)

    return service.login(request)


@router.post(
    "/staff-login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
def staff_login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    service = AuthService(db)

    return service.login_staff(request)