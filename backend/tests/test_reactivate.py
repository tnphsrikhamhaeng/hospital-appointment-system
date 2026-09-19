import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.enums import (
    DepartmentStatusEnum,
    DoctorStatusEnum,
    SpecializationStatusEnum,
    UserRoleEnum,
    UserStatusEnum,
)
from app.main import app
from app.models.department import Department
from app.models.doctor import Doctor
from app.models.specialization import Specialization
from app.models.user import User


client = TestClient(app)


def get_staff_credentials() -> tuple[str, str]:
    """
    Read credentials for an existing Hospital Staff account.

    The test must use a real account from the project's database.
    No user is created and no password is guessed.
    """
    username = os.getenv("TEST_STAFF_USERNAME")
    password = os.getenv("TEST_STAFF_PASSWORD")

    if not username or not password:
        pytest.skip(
            "Set TEST_STAFF_USERNAME and TEST_STAFF_PASSWORD "
            "to an existing active Hospital Staff account."
        )

    return username, password


def login_staff() -> tuple[str, str]:
    """
    Login through the real Hospital Staff authentication endpoint.
    """
    username, password = get_staff_credentials()

    response = client.post(
        "/auth/staff-login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 200, (
        "Hospital Staff login failed: "
        f"{response.status_code} {response.text}"
    )

    data = response.json()

    assert "access_token" in data

    return data["access_token"], password


@pytest.fixture(scope="module")
def staff_auth():
    return login_staff()


def auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
    }


def get_inactive_doctor(db):
    return db.scalar(
        select(Doctor).where(
            Doctor.status == DoctorStatusEnum.INACTIVE,
        )
    )


def get_inactive_department(db):
    return db.scalar(
        select(Department).where(
            Department.status == DepartmentStatusEnum.INACTIVE,
        )
    )


def get_inactive_specialization(db):
    return db.scalar(
        select(Specialization).where(
            Specialization.status
            == SpecializationStatusEnum.INACTIVE,
        )
    )


def get_inactive_staff(db):
    return db.scalar(
        select(User).where(
            User.role == UserRoleEnum.HOSPITAL_STAFF,
            User.status == UserStatusEnum.INACTIVE,
        )
    )


def get_active_doctor(db):
    return db.scalar(
        select(Doctor).where(
            Doctor.status == DoctorStatusEnum.ACTIVE,
        )
    )


def get_active_department(db):
    return db.scalar(
        select(Department).where(
            Department.status == DepartmentStatusEnum.ACTIVE,
        )
    )


def get_active_specialization(db):
    return db.scalar(
        select(Specialization).where(
            Specialization.status
            == SpecializationStatusEnum.ACTIVE,
        )
    )


def get_active_staff(db):
    return db.scalar(
        select(User).where(
            User.role == UserRoleEnum.HOSPITAL_STAFF,
            User.status == UserStatusEnum.ACTIVE,
        )
    )


def test_reactivate_doctor_success(staff_auth):
    token, password = staff_auth

    with SessionLocal() as db:
        doctor = get_inactive_doctor(db)

        if doctor is None:
            pytest.skip(
                "No inactive doctor exists in the real database."
            )

        response = client.post(
            "/reactivate",
            headers=auth_headers(token),
            json={
                "target_type": "doctor",
                "target_id": str(doctor.id),
                "password": password,
            },
        )

        assert response.status_code == 200

        db.expire_all()

        updated = db.get(Doctor, doctor.id)

        assert updated is not None
        assert updated.status == DoctorStatusEnum.ACTIVE


def test_reactivate_department_success(staff_auth):
    token, password = staff_auth

    with SessionLocal() as db:
        department = get_inactive_department(db)

        if department is None:
            pytest.skip(
                "No inactive department exists in the real database."
            )

        response = client.post(
            "/reactivate",
            headers=auth_headers(token),
            json={
                "target_type": "department",
                "target_id": str(department.id),
                "password": password,
            },
        )

        assert response.status_code == 200

        db.expire_all()

        updated = db.get(Department, department.id)

        assert updated is not None
        assert updated.status == DepartmentStatusEnum.ACTIVE


def test_reactivate_specialization_success(staff_auth):
    token, password = staff_auth

    with SessionLocal() as db:
        specialization = get_inactive_specialization(db)

        if specialization is None:
            pytest.skip(
                "No inactive specialization exists in the real database."
            )

        response = client.post(
            "/reactivate",
            headers=auth_headers(token),
            json={
                "target_type": "specialization",
                "target_id": str(specialization.id),
                "password": password,
            },
        )

        assert response.status_code == 200

        db.expire_all()

        updated = db.get(
            Specialization,
            specialization.id,
        )

        assert updated is not None
        assert updated.status == SpecializationStatusEnum.ACTIVE


def test_reactivate_staff_success(staff_auth):
    token, password = staff_auth

    with SessionLocal() as db:
        staff = get_inactive_staff(db)

        if staff is None:
            pytest.skip(
                "No inactive Hospital Staff exists in the real database."
            )

        response = client.post(
            "/reactivate",
            headers=auth_headers(token),
            json={
                "target_type": "staff",
                "target_id": str(staff.id),
                "password": password,
            },
        )

        assert response.status_code == 200

        db.expire_all()

        updated = db.get(User, staff.id)

        assert updated is not None
        assert updated.status == UserStatusEnum.ACTIVE


@pytest.mark.parametrize(
    "target_type",
    [
        "doctor",
        "department",
        "specialization",
        "staff",
    ],
)
def test_reactivate_wrong_password(target_type, staff_auth):
    token, _ = staff_auth

    with SessionLocal() as db:
        if target_type == "doctor":
            target = get_inactive_doctor(db)
        elif target_type == "department":
            target = get_inactive_department(db)
        elif target_type == "specialization":
            target = get_inactive_specialization(db)
        else:
            target = get_inactive_staff(db)

        if target is None:
            pytest.skip(
                f"No inactive {target_type} exists in the real database."
            )

        response = client.post(
            "/reactivate",
            headers=auth_headers(token),
            json={
                "target_type": target_type,
                "target_id": str(target.id),
                "password": "wrong-password-for-reactivate-test",
            },
        )

        assert response.status_code == 400


@pytest.mark.parametrize(
    "target_type",
    [
        "doctor",
        "department",
        "specialization",
        "staff",
    ],
)
def test_reactivate_not_found(target_type, staff_auth):
    token, password = staff_auth

    response = client.post(
        "/reactivate",
        headers=auth_headers(token),
        json={
            "target_type": target_type,
            "target_id": str(uuid.uuid4()),
            "password": password,
        },
    )

    assert response.status_code == 404


def test_reactivate_active_doctor(staff_auth):
    token, password = staff_auth

    with SessionLocal() as db:
        doctor = get_active_doctor(db)

        if doctor is None:
            pytest.skip(
                "No active doctor exists in the real database."
            )

        response = client.post(
            "/reactivate",
            headers=auth_headers(token),
            json={
                "target_type": "doctor",
                "target_id": str(doctor.id),
                "password": password,
            },
        )

        assert response.status_code == 400


def test_reactivate_active_department(staff_auth):
    token, password = staff_auth

    with SessionLocal() as db:
        department = get_active_department(db)

        if department is None:
            pytest.skip(
                "No active department exists in the real database."
            )

        response = client.post(
            "/reactivate",
            headers=auth_headers(token),
            json={
                "target_type": "department",
                "target_id": str(department.id),
                "password": password,
            },
        )

        assert response.status_code == 400


def test_reactivate_active_specialization(staff_auth):
    token, password = staff_auth

    with SessionLocal() as db:
        specialization = get_active_specialization(db)

        if specialization is None:
            pytest.skip(
                "No active specialization exists in the real database."
            )

        response = client.post(
            "/reactivate",
            headers=auth_headers(token),
            json={
                "target_type": "specialization",
                "target_id": str(specialization.id),
                "password": password,
            },
        )

        assert response.status_code == 400


def test_reactivate_active_staff(staff_auth):
    token, password = staff_auth

    with SessionLocal() as db:
        staff = get_active_staff(db)

        if staff is None:
            pytest.skip(
                "No active Hospital Staff exists in the real database."
            )

        response = client.post(
            "/reactivate",
            headers=auth_headers(token),
            json={
                "target_type": "staff",
                "target_id": str(staff.id),
                "password": password,
            },
        )

        assert response.status_code == 400


@pytest.mark.parametrize(
    "payload",
    [
        {
            "target_type": "invalid",
            "target_id": "00000000-0000-0000-0000-000000000000",
            "password": "Test@1234",
        },
        {
            "target_type": "doctor",
            "target_id": "not-a-uuid",
            "password": "Test@1234",
        },
        {
            "target_type": "doctor",
            "target_id": "00000000-0000-0000-0000-000000000000",
            "password": "",
        },
        {
            "target_type": "doctor",
            "target_id": "00000000-0000-0000-0000-000000000000",
            "password": "Test@1234",
            "extra": "forbidden",
        },
    ],
)
def test_reactivate_validation(payload, staff_auth):
    token, _ = staff_auth

    response = client.post(
        "/reactivate",
        headers=auth_headers(token),
        json=payload,
    )

    assert response.status_code == 422


def test_reactivate_requires_authentication():
    response = client.post(
        "/reactivate",
        json={
            "target_type": "doctor",
            "target_id": str(uuid.uuid4()),
            "password": "Test@1234",
        },
    )

    assert response.status_code == 401


def test_reactivate_forbidden_for_patient():
    """
    Authorization check for a non-staff user.

    A real patient account must be supplied through environment variables.
    No patient is created by this test.
    """
    username = os.getenv("TEST_PATIENT_USERNAME")
    password = os.getenv("TEST_PATIENT_PASSWORD")

    if not username or not password:
        pytest.skip(
            "Set TEST_PATIENT_USERNAME and TEST_PATIENT_PASSWORD "
            "to an existing active Patient account."
        )

    response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    response = client.post(
        "/reactivate",
        headers=auth_headers(token),
        json={
            "target_type": "doctor",
            "target_id": str(uuid.uuid4()),
            "password": password,
        },
    )

    assert response.status_code == 403
