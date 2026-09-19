import os
import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

STAFF_USERNAME = os.getenv("teststaff01")
STAFF_PASSWORD = os.getenv("test12345678*")



@pytest.fixture
def staff_token():
    if not STAFF_USERNAME or not STAFF_PASSWORD:
        pytest.skip(
            "TEST_STAFF_USERNAME / TEST_STAFF_PASSWORD are not configured"
        )

    response = client.post(
        "/auth/staff-login",
        json={
            "username": STAFF_USERNAME,
            "password": STAFF_PASSWORD,
        },
    )

    if response.status_code != 200:
        pytest.skip(
            f"Unable to login test staff: "
            f"{response.status_code} {response.text}"
        )

    return response.json()["access_token"]


@pytest.fixture
def staff_headers(staff_token):
    return {
        "Authorization": f"Bearer {staff_token}",
        "Content-Type": "application/json",
    }


@pytest.fixture
def existing_specialization_id(staff_headers):
    """
    ใช้ Specialization ที่มีอยู่จริงจากระบบ
    """
    response = client.get(
        "/specializations",
        headers=staff_headers,
    )

    assert response.status_code == 200

    data = response.json()

    if isinstance(data, dict):
        items = data.get("items", data.get("data", []))
    else:
        items = data

    if not items:
        pytest.skip("No specialization exists in database")

    return items[0]["id"]


# ============================================================
# QA-15.5.1 Delete active specialization
# ============================================================

def test_delete_active_specialization(
    staff_headers,
    existing_specialization_id,
):
    response = client.delete(
        f"/specializations/{existing_specialization_id}",
        headers=staff_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == existing_specialization_id
    assert data["status"] == "INACTIVE"


# ============================================================
# QA-15.5.2 Verify soft delete
# ============================================================

def test_deleted_specialization_is_inactive(
    staff_headers,
    existing_specialization_id,
):
    response = client.get(
        f"/specializations/{existing_specialization_id}",
        headers=staff_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == existing_specialization_id
    assert data["status"] == "INACTIVE"


# ============================================================
# QA-15.5.3 Delete already inactive specialization
# ============================================================

def test_delete_already_inactive_specialization(
    staff_headers,
    existing_specialization_id,
):
    response = client.delete(
        f"/specializations/{existing_specialization_id}",
        headers=staff_headers,
    )

    assert response.status_code in (400, 409)


# ============================================================
# QA-15.5.4 Delete nonexistent specialization
# ============================================================

def test_delete_nonexistent_specialization(
    staff_headers,
):
    nonexistent_id = str(uuid.uuid4())

    response = client.delete(
        f"/specializations/{nonexistent_id}",
        headers=staff_headers,
    )

    assert response.status_code == 404


# ============================================================
# QA-15.5.5 Invalid UUID
# ============================================================

def test_delete_specialization_invalid_uuid(
    staff_headers,
):
    response = client.delete(
        "/specializations/not-a-valid-uuid",
        headers=staff_headers,
    )

    assert response.status_code == 422


# ============================================================
# QA-15.5.6 No authentication
# ============================================================

def test_delete_specialization_without_auth(
    staff_headers,
    existing_specialization_id,
):
    response = client.delete(
        f"/specializations/{existing_specialization_id}",
    )

    assert response.status_code == 401


# ============================================================
# QA-15.5.7 Patient forbidden
# ============================================================

def test_delete_specialization_patient_forbidden(
    existing_specialization_id,
):
    pytest.skip(
        "Requires a real Patient account credential. "
        "Manual Functional Test should verify 403 Forbidden."
    )