import pytest
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.main import app
from app.core.database import SessionLocal
from app.core.enums import UserRoleEnum
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.utils.security import verify_password

client = TestClient(app)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(db, role=None):
    stmt = select(User)
    if role is not None:
        stmt = stmt.where(User.role == role)
    return db.scalar(stmt)


def cleanup_tokens(db):
    db.execute(delete(PasswordResetToken))
    db.commit()


@pytest.fixture(autouse=True)
def clean_tokens():
    with SessionLocal() as db:
        cleanup_tokens(db)
    yield
    with SessionLocal() as db:
        cleanup_tokens(db)


def test_forgot_password_success():
    with SessionLocal() as db:
        user = get_user(db)
        assert user is not None

        response = client.post(
            "/auth/forgot-password",
            json={"email": user.email},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password reset token generated"
        assert data["reset_token"]

        token = db.scalar(
            select(PasswordResetToken).where(
                PasswordResetToken.token == data["reset_token"]
            )
        )
        assert token is not None
        assert token.user_id == user.id
        assert token.used_at is None

        now = datetime.now(timezone.utc)
        expires_at = token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        remaining = expires_at - now
        assert timedelta(minutes=14) <= remaining <= timedelta(minutes=16)


def test_forgot_password_user_not_found():
    response = client.post(
        "/auth/forgot-password",
        json={"email": "not-found@example.com"},
    )

    assert response.status_code in (400, 404)


def test_forgot_password_invalid_email():
    response = client.post(
        "/auth/forgot-password",
        json={"email": "invalid-email"},
    )

    assert response.status_code == 422


def test_forgot_password_extra_field_forbidden():
    with SessionLocal() as db:
        user = get_user(db)
        assert user is not None

        response = client.post(
            "/auth/forgot-password",
            json={
                "email": user.email,
                "extra": "forbidden",
            },
        )

        assert response.status_code == 422


@pytest.mark.parametrize(
    "role",
    [
        UserRoleEnum.DOCTOR,
        UserRoleEnum.HOSPITAL_STAFF,
    ],
)
def test_staff_forgot_password_success(role):
    with SessionLocal() as db:
        user = get_user(db, role)
        assert user is not None
        assert user.username

        response = client.post(
            "/auth/staff-forgot-password",
            json={"username": user.username},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password reset token generated"
        assert data["reset_token"]

        token = db.scalar(
            select(PasswordResetToken).where(
                PasswordResetToken.token == data["reset_token"]
            )
        )
        assert token is not None
        assert token.user_id == user.id
        assert token.used_at is None


def test_staff_forgot_password_non_staff_forbidden():
    with SessionLocal() as db:
        user = get_user(db, UserRoleEnum.PATIENT)
        assert user is not None
        assert user.username

        response = client.post(
            "/auth/staff-forgot-password",
            json={"username": user.username},
        )

        assert response.status_code in (401, 403)


def test_staff_forgot_password_user_not_found():
    response = client.post(
        "/auth/staff-forgot-password",
        json={"username": "not-found-user"},
    )

    assert response.status_code in (400, 404)


def test_staff_forgot_password_validation():
    response = client.post(
        "/auth/staff-forgot-password",
        json={"username": ""},
    )
    assert response.status_code == 422

    response = client.post(
        "/auth/staff-forgot-password",
        json={
            "username": "valid-user",
            "extra": "forbidden",
        },
    )
    assert response.status_code == 422


def create_reset_token(user_id, *, expires_at=None, used_at=None):
    with SessionLocal() as db:
        token = PasswordResetToken(
            user_id=user_id,
            token=f"qa-{datetime.now(timezone.utc).timestamp()}",
            expires_at=expires_at
            or datetime.now(timezone.utc) + timedelta(minutes=15),
            used_at=used_at,
        )
        db.add(token)
        db.commit()
        db.refresh(token)
        return token.token


def test_reset_password_success():
    with SessionLocal() as db:
        user = get_user(db)
        assert user is not None
        token_value = create_reset_token(user.id)

        response = client.post(
            "/auth/reset-password",
            json={
                "reset_token": token_value,
                "new_password": "NewStrong123!",
                "confirm_password": "NewStrong123!",
            },
        )

        assert response.status_code == 204

        db.expire_all()
        token = db.scalar(
            select(PasswordResetToken).where(
                PasswordResetToken.token == token_value
            )
        )
        user = db.get(User, user.id)

        assert token is not None
        assert token.used_at is not None
        assert user is not None
        assert verify_password("NewStrong123!", user.password)


def test_reset_password_invalid_token():
    response = client.post(
        "/auth/reset-password",
        json={
            "reset_token": "invalid-reset-token",
            "new_password": "NewStrong123!",
            "confirm_password": "NewStrong123!",
        },
    )

    assert response.status_code in (400, 404)


def test_reset_password_used_token():
    with SessionLocal() as db:
        user = get_user(db)
        assert user is not None
        token_value = create_reset_token(
            user.id,
            used_at=datetime.now(timezone.utc),
        )

        response = client.post(
            "/auth/reset-password",
            json={
                "reset_token": token_value,
                "new_password": "NewStrong123!",
                "confirm_password": "NewStrong123!",
            },
        )

        assert response.status_code in (400, 409)


def test_reset_password_expired_token():
    with SessionLocal() as db:
        user = get_user(db)
        assert user is not None
        token_value = create_reset_token(
            user.id,
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        )

        response = client.post(
            "/auth/reset-password",
            json={
                "reset_token": token_value,
                "new_password": "NewStrong123!",
                "confirm_password": "NewStrong123!",
            },
        )

        assert response.status_code in (400, 409)


@pytest.mark.parametrize(
    "new_password,confirm_password",
    [
        ("NewStrong123!", "Different123!"),
        ("short", "short"),
    ],
)
def test_reset_password_validation(new_password, confirm_password):
    with SessionLocal() as db:
        user = get_user(db)
        assert user is not None
        token_value = create_reset_token(user.id)

        response = client.post(
            "/auth/reset-password",
            json={
                "reset_token": token_value,
                "new_password": new_password,
                "confirm_password": confirm_password,
            },
        )

        assert response.status_code == 422


def test_reset_password_extra_field_forbidden():
    with SessionLocal() as db:
        user = get_user(db)
        assert user is not None
        token_value = create_reset_token(user.id)

        response = client.post(
            "/auth/reset-password",
            json={
                "reset_token": token_value,
                "new_password": "NewStrong123!",
                "confirm_password": "NewStrong123!",
                "extra": "forbidden",
            },
        )

        assert response.status_code == 422
