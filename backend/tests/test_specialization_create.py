import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.enums import (
    SpecializationStatusEnum,
    UserRoleEnum,
)
from app.main import app
from app.models.department import Department
from app.models.specialization import Specialization


client = TestClient(app)


def login_staff() -> str:
    username = os.getenv("teststaff01")
    password = os.getenv("test12345678*")

    if not username or not password:
        pytest.skip(
            "Set TEST_STAFF_USERNAME and TEST_STAFF_PASSWORD "
            "to an existing active Hospital Staff account."
        )

    response = client.post(
        "/auth/staff-login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

    return data["access_token"]


@pytest.fixture(scope="module")
def staff_token():
    return login_staff()


def auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
    }


def get_department(db):
    return db.scalar(
        select(Department).order_by(Department.created_at)
    )


def get_second_department(db, first_department_id):
    return db.scalar(
        select(Department).where(
            Department.id != first_department_id
        ).order_by(Department.created_at)
    )


def test_create_specialization_success(staff_token):
    with SessionLocal() as db:
        department = get_department(db)

        if department is None:
            pytest.skip(
                "No department exists in the real database."
            )

        name = f"QA Specialization {uuid.uuid4().hex[:8]}"

        response = client.post(
            "/specializations",
            headers=auth_headers(staff_token),
            json={
                "name": name,
                "description": "QA specialization",
                "department_id": str(department.id),
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["name"] == name
        assert data["description"] == "QA specialization"
        assert data["department_id"] == str(department.id)
        assert data["status"] == SpecializationStatusEnum.ACTIVE.value

        created = db.get(
            Specialization,
            uuid.UUID(data["id"]),
        )

        assert created is not None
        assert created.status == SpecializationStatusEnum.ACTIVE

        db.rollback()


def test_create_specialization_name_normalization(staff_token):
    with SessionLocal() as db:
        department = get_department(db)

        if department is None:
            pytest.skip(
                "No department exists in the real database."
            )

        response = client.post(
            "/specializations",
            headers=auth_headers(staff_token),
            json={
                "name": "  QA   Normalized   Name  ",
                "description": "  Test   Description  ",
                "department_id": str(department.id),
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["name"] == "QA Normalized Name"
        assert data["description"] == "Test Description"

        db.rollback()


def test_create_specialization_department_not_found(staff_token):
    response = client.post(
        "/specializations",
        headers=auth_headers(staff_token),
        json={
            "name": f"QA Missing Department {uuid.uuid4().hex[:8]}",
            "description": "QA test",
            "department_id": str(uuid.uuid4()),
        },
    )

    assert response.status_code == 404


def test_create_specialization_duplicate_name_same_department(
    staff_token,
):
    with SessionLocal() as db:
        department = get_department(db)

        if department is None:
            pytest.skip(
                "No department exists in the real database."
            )

        existing = db.scalar(
            select(Specialization).where(
                Specialization.department_id == department.id
            )
        )

        if existing is None:
            pytest.skip(
                "No specialization exists in the selected department."
            )

        response = client.post(
            "/specializations",
            headers=auth_headers(staff_token),
            json={
                "name": existing.name,
                "description": "Duplicate test",
                "department_id": str(department.id),
            },
        )

        assert response.status_code == 409


def test_create_specialization_same_name_different_department(
    staff_token,
):
    with SessionLocal() as db:
        first_department = get_department(db)

        if first_department is None:
            pytest.skip(
                "No department exists in the real database."
            )

        second_department = get_second_department(
            db,
            first_department.id,
        )

        if second_department is None:
            pytest.skip(
                "At least two departments are required for this test."
            )

        existing = db.scalar(
            select(Specialization).where(
                Specialization.department_id == first_department.id
            )
        )

        if existing is None:
            pytest.skip(
                "No specialization exists in the first department."
            )

        response = client.post(
            "/specializations",
            headers=auth_headers(staff_token),
            json={
                "name": existing.name,
                "description": "Different department test",
                "department_id": str(second_department.id),
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["name"] == existing.name
        assert data["department_id"] == str(second_department.id)

        db.rollback()


@pytest.mark.parametrize(
    "payload",
    [
        {
            "name": "A",
            "description": "Too short name",
        },
        {
            "name": "",
            "description": "Empty name",
        },
        {
            "name": "Valid Name",
            "description": "x" * 501,
        },
    ],
)
def test_create_specialization_validation(
    payload,
    staff_token,
):
    with SessionLocal() as db:
        department = get_department(db)

        if department is None:
            pytest.skip(
                "No department exists in the real database."
            )

        payload["department_id"] = str(department.id)

    response = client.post(
        "/specializations",
        headers=auth_headers(staff_token),
        json=payload,
    )

    assert response.status_code == 422


def test_create_specialization_extra_field_forbidden(
    staff_token,
):
    with SessionLocal() as db:
        department = get_department(db)

        if department is None:
            pytest.skip(
                "No department exists in the real database."
            )

        payload = {
            "name": f"QA Extra Field {uuid.uuid4().hex[:8]}",
            "description": "QA test",
            "department_id": str(department.id),
            "extra": "not allowed",
        }

    response = client.post(
        "/specializations",
        headers=auth_headers(staff_token),
        json=payload,
    )

    assert response.status_code == 422


def test_create_specialization_requires_authentication():
    with SessionLocal() as db:
        department = get_department(db)

        if department is None:
            pytest.skip(
                "No department exists in the real database."
            )

        response = client.post(
            "/specializations",
            json={
                "name": f"QA Unauthorized {uuid.uuid4().hex[:8]}",
                "description": "QA test",
                "department_id": str(department.id),
            },
        )

    assert response.status_code == 401


def test_create_specialization_patient_forbidden():
    username = os.getenv("ken04")
    password = os.getenv("Ken12345678@")

    if not username or not password:
        pytest.skip(
            "Set TEST_PATIENT_USERNAME and TEST_PATIENT_PASSWORD "
            "to an existing active Patient account."
        )

    with SessionLocal() as db:
        department = get_department(db)

        if department is None:
            pytest.skip(
                "No department exists in the real database."
            )

    login_response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    patient_token = login_response.json()["access_token"]

    response = client.post(
        "/specializations",
        headers=auth_headers(patient_token),
        json={
            "name": f"QA Forbidden {uuid.uuid4().hex[:8]}",
            "description": "QA test",
            "department_id": str(department.id),
        },
    )

    assert response.status_code == 403
