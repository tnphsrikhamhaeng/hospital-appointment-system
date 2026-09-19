import uuid

import pytest
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.exceptions import InvalidCredentialsException
from app.models.user import User
from app.schemas.change_password import ChangePasswordRequest
from app.services.change_password_service import ChangePasswordService
from app.utils.security import verify_password


def get_test_user(db):
    user = db.scalar(
        select(User).limit(1)
    )

    if user is None:
        pytest.skip("No user found for change password test.")

    return user


def test_change_password_success():
    db = SessionLocal()

    try:
        user = get_test_user(db)

        original_password_hash = user.password
        current_password = "Test@1234"
        new_password = "NewTest@5678"

        user.password = (
            __import__(
                "app.utils.security",
                fromlist=["hash_password"],
            ).hash_password(current_password)
        )
        db.flush()

        service = ChangePasswordService(db)

        request = ChangePasswordRequest(
            current_password=current_password,
            new_password=new_password,
            confirm_password=new_password,
        )

        service.change_password(
            current_user=user,
            request=request,
        )

        assert user.password != original_password_hash
        assert user.password != new_password

        assert verify_password(
            plain_password=new_password,
            hashed_password=user.password,
        )

        assert not verify_password(
            plain_password=current_password,
            hashed_password=user.password,
        )

        db.rollback()

    finally:
        db.rollback()
        db.close()


def test_change_password_wrong_current_password():
    db = SessionLocal()

    try:
        user = get_test_user(db)

        service = ChangePasswordService(db)

        request = ChangePasswordRequest(
            current_password="Wrong@1234",
            new_password="NewTest@5678",
            confirm_password="NewTest@5678",
        )

        with pytest.raises(InvalidCredentialsException):
            service.change_password(
                current_user=user,
                request=request,
            )

        db.rollback()

    finally:
        db.close()


def test_change_password_user_not_found():
    db = SessionLocal()

    try:
        service = ChangePasswordService(db)

        fake_user = User(
            id=uuid.uuid4(),
        )

        request = ChangePasswordRequest(
            current_password="Test@1234",
            new_password="NewTest@5678",
            confirm_password="NewTest@5678",
        )

        with pytest.raises(InvalidCredentialsException):
            service.change_password(
                current_user=fake_user,
                request=request,
            )

    finally:
        db.close()


def test_change_password_mismatch():
    with pytest.raises(ValueError):
        ChangePasswordRequest(
            current_password="Test@1234",
            new_password="NewTest@5678",
            confirm_password="Different@1234",
        )


def test_change_password_weak_new_password():
    with pytest.raises(ValueError):
        ChangePasswordRequest(
            current_password="Test@1234",
            new_password="NewTest1234",
            confirm_password="NewTest1234",
        )


def test_change_password_extra_field_forbidden():
    with pytest.raises(ValueError):
        ChangePasswordRequest(
            current_password="Test@1234",
            new_password="NewTest@5678",
            confirm_password="NewTest@5678",
            username="not_allowed",
        )