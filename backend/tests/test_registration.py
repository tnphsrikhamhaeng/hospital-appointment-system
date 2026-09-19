import uuid
from datetime import date

import pytest
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.enums import UserRoleEnum, UserStatusEnum
from app.core.exceptions import (
    EmailAlreadyExistsException,
    PhoneNumberAlreadyExistsException,
    UsernameAlreadyExistsException,
)
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.services.auth_service import AuthService
from app.utils.security import verify_password


def build_register_request(
    username: str | None = None,
    email: str | None = None,
    phone_number: str | None = None,
    password: str = "Test@1234",
    confirm_password: str | None = None,
) -> RegisterRequest:
    username = username or f"test_{uuid.uuid4().hex[:8]}"
    email = email or f"{uuid.uuid4().hex[:8]}@example.com"
    phone_number = phone_number or "08" + str(uuid.uuid4().int)[-8:]

    return RegisterRequest(
        username=username,
        first_name="Test",
        last_name="User",
        date_of_birth=date(2000, 1, 1),
        gender="male",
        phone_number=phone_number,
        email=email,
        password=password,
        confirm_password=(
            confirm_password
            if confirm_password is not None
            else password
        ),
    )


def test_register_success():
    db = SessionLocal()

    try:
        service = AuthService(db)
        request = build_register_request()

        result = service.register(request)

        user = db.scalar(
            select(User).where(
                User.id == result.id
            )
        )

        assert user is not None
        assert user.username == request.username
        assert user.email == request.email
        assert user.phone_number == request.phone_number
        assert user.role == UserRoleEnum.PATIENT
        assert user.status == UserStatusEnum.ACTIVE

        assert user.password != request.password
        assert verify_password(
            plain_password=request.password,
            hashed_password=user.password,
        )

        db.rollback()

    finally:
        db.close()


def test_register_duplicate_username():
    db = SessionLocal()

    try:
        service = AuthService(db)

        first_request = build_register_request()
        service.register(first_request)

        second_request = build_register_request(
            username=first_request.username,
        )

        with pytest.raises(
            UsernameAlreadyExistsException
        ):
            service.register(second_request)

        db.rollback()

    finally:
        db.close()


def test_register_duplicate_email():
    db = SessionLocal()

    try:
        service = AuthService(db)

        first_request = build_register_request()
        service.register(first_request)

        second_request = build_register_request(
            email=first_request.email,
        )

        with pytest.raises(
            EmailAlreadyExistsException
        ):
            service.register(second_request)

        db.rollback()

    finally:
        db.close()


def test_register_duplicate_phone_number():
    db = SessionLocal()

    try:
        service = AuthService(db)

        first_request = build_register_request()
        service.register(first_request)

        second_request = build_register_request(
            phone_number=first_request.phone_number,
        )

        with pytest.raises(
            PhoneNumberAlreadyExistsException
        ):
            service.register(second_request)

        db.rollback()

    finally:
        db.close()


def test_register_password_mismatch():
    with pytest.raises(ValueError):
        build_register_request(
            password="Test@1234",
            confirm_password="Test@5678",
        )


def test_register_weak_password():
    with pytest.raises(ValueError):
        build_register_request(
            password="Test1234",
        )


def test_register_future_date_of_birth():
    with pytest.raises(ValueError):
        RegisterRequest(
            username=f"test_{uuid.uuid4().hex[:8]}",
            first_name="Test",
            last_name="User",
            date_of_birth=date.today().replace(
                year=date.today().year + 1
            ),
            gender="male",
            phone_number="0812345678",
            email=f"{uuid.uuid4().hex[:8]}@example.com",
            password="Test@1234",
            confirm_password="Test@1234",
        )


def test_register_username_normalization():
    request = build_register_request(
        username="  Test_User  ",
    )

    assert request.username == "test_user"