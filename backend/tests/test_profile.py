import uuid

import pytest
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.exceptions import (
    EmailAlreadyExistsException,
    PhoneNumberAlreadyExistsException,
    UserNotFoundException,
)
from app.core.enums import GenderEnum
from app.models.user import User
from app.schemas.user import UpdateProfileRequest
from app.services.profile_service import ProfileService


def get_test_users(db):
    users = list(
        db.scalars(
            select(User)
            .where(User.email.is_not(None))
            .limit(2)
        ).all()
    )

    if len(users) < 2:
        pytest.skip("Need at least 2 users for profile tests.")

    return users[0], users[1]


def test_get_profile():
    db = SessionLocal()

    try:
        user, _ = get_test_users(db)

        service = ProfileService(db)

        result = service.get_profile(user)

        assert result.id == user.id
        assert result.username == user.username
        assert result.email == user.email
        assert result.first_name == user.first_name
        assert result.last_name == user.last_name
        assert result.phone_number == user.phone_number

    finally:
        db.close()


def test_get_profile_user_not_found():
    db = SessionLocal()

    try:
        service = ProfileService(db)

        fake_user = User(
            id=uuid.uuid4(),
        )

        with pytest.raises(UserNotFoundException):
            service.get_profile(fake_user)

    finally:
        db.close()


def test_update_profile():
    db = SessionLocal()

    try:
        user, _ = get_test_users(db)

        original_first_name = user.first_name
        original_last_name = user.last_name
        original_phone = user.phone_number
        original_email = user.email

        service = ProfileService(db)

        request = UpdateProfileRequest(
            first_name="Updated",
            last_name="Profile",
        )

        result = service.update_profile(
            current_user=user,
            request=request,
        )

        assert result.id == user.id
        assert result.first_name == "Updated"
        assert result.last_name == "Profile"

        db.rollback()

        user.first_name = original_first_name
        user.last_name = original_last_name
        user.phone_number = original_phone
        user.email = original_email

    finally:
        db.rollback()
        db.close()


def test_update_profile_email_duplicate():
    db = SessionLocal()

    try:
        user, other_user = get_test_users(db)

        service = ProfileService(db)

        request = UpdateProfileRequest(
            email=other_user.email,
        )

        with pytest.raises(EmailAlreadyExistsException):
            service.update_profile(
                current_user=user,
                request=request,
            )

        db.rollback()

    finally:
        db.close()


def test_update_profile_phone_duplicate():
    db = SessionLocal()

    try:
        user, other_user = get_test_users(db)

        service = ProfileService(db)

        request = UpdateProfileRequest(
            phone_number=other_user.phone_number,
        )

        with pytest.raises(PhoneNumberAlreadyExistsException):
            service.update_profile(
                current_user=user,
                request=request,
            )

        db.rollback()

    finally:
        db.close()


def test_update_profile_same_email():
    db = SessionLocal()

    try:
        user, _ = get_test_users(db)

        service = ProfileService(db)

        request = UpdateProfileRequest(
            email=user.email,
        )

        result = service.update_profile(
            current_user=user,
            request=request,
        )

        assert result.email == user.email

        db.rollback()

    finally:
        db.close()


def test_update_profile_same_phone():
    db = SessionLocal()

    try:
        user, _ = get_test_users(db)

        service = ProfileService(db)

        request = UpdateProfileRequest(
            phone_number=user.phone_number,
        )

        result = service.update_profile(
            current_user=user,
            request=request,
        )

        assert result.phone_number == user.phone_number

        db.rollback()

    finally:
        db.close()


def test_update_profile_validation():
    with pytest.raises(ValueError):
        UpdateProfileRequest(
            first_name="A",
        )

    with pytest.raises(ValueError):
        UpdateProfileRequest(
            last_name="A",
        )

    with pytest.raises(ValueError):
        UpdateProfileRequest(
            phone_number="123",
        )

    with pytest.raises(ValueError):
        UpdateProfileRequest(
            email="invalid-email",
        )


def test_update_profile_extra_field_forbidden():
    with pytest.raises(ValueError):
        UpdateProfileRequest(
            username="not_allowed",
        )