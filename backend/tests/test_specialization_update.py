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
# QA-15.4.1 Update name
# ============================================================

def test_update_specialization_name(
    staff_headers,
    existing_specialization_id,
):
    new_name = f"Updated Specialization {uuid.uuid4().hex[:8]}"

    response = client.patch(
        f"/specializations/{existing_specialization_id}",
        headers=staff_headers,
        json={
            "name": new_name,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == existing_specialization_id
    assert data["name"] == new_name


# ============================================================
# QA-15.4.2 Update description
# ============================================================

def test_update_specialization_description(
    staff_headers,
    existing_specialization_id,
):
    new_description = (
        f"Updated description {uuid.uuid4().hex[:8]}"
    )

    response = client.patch(
        f"/specializations/{existing_specialization_id}",
        headers=staff_headers,
        json={
            "description": new_description,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == existing_specialization_id
    assert data["description"] == new_description


# ============================================================
# QA-15.4.3 Update multiple fields
# ============================================================

def test_update_specialization_multiple_fields(
    staff_headers,
    existing_specialization_id,
):
    new_name = f"Updated Multi {uuid.uuid4().hex[:8]}"
    new_description = f"Updated multi description {uuid.uuid4().hex[:8]}"

    response = client.patch(
        f"/specializations/{existing_specialization_id}",
        headers=staff_headers,
        json={
            "name": new_name,
            "description": new_description,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == existing_specialization_id
    assert data["name"] == new_name
    assert data["description"] == new_description


# ============================================================
# QA-15.4.4 Update nonexistent specialization
# ============================================================

def test_update_nonexistent_specialization(
    staff_headers,
):
    nonexistent_id = str(uuid.uuid4())

    response = client.patch(
        f"/specializations/{nonexistent_id}",
        headers=staff_headers,
        json={
            "name": "Nonexistent Specialization",
        },
    )

    assert response.status_code == 404


# ============================================================
# QA-15.4.5 Invalid name validation
# ============================================================

@pytest.mark.parametrize(
    "invalid_name",
    [
        "",
        "A",
    ],
)
def test_update_invalid_name(
    staff_headers,
    existing_specialization_id,
    invalid_name,
):
    response = client.patch(
        f"/specializations/{existing_specialization_id}",
        headers=staff_headers,
        json={
            "name": invalid_name,
        },
    )

    assert response.status_code == 422


# ============================================================
# QA-15.4.6 Duplicate name in same department
# ============================================================

def test_update_duplicate_specialization_name(
    staff_headers,
):
    response = client.get("/specializations")

    assert response.status_code == 200

    data = response.json()

    if isinstance(data, dict):
        items = data.get("items", data.get("data", []))
    else:
        items = data

    if len(items) < 2:
        pytest.skip(
            "At least two specializations are required "
            "for duplicate-name test"
        )

    first = items[0]
    second = items[1]

    if first["department_id"] != second["department_id"]:
        pytest.skip(
            "Need two specializations in the same department"
        )

    response = client.patch(
        f"/specializations/{second['id']}",
        headers=staff_headers,
        json={
            "name": first["name"],
        },
    )

    assert response.status_code in (400, 409)


# ============================================================
# QA-15.4.7 No authentication
# ============================================================

def test_update_specialization_without_auth(
    existing_specialization_id,
):
    response = client.patch(
        f"/specializations/{existing_specialization_id}",
        json={
            "name": "Unauthorized Update",
        },
    )

    assert response.status_code == 401


# ============================================================
# QA-15.4.8 Invalid UUID
# ============================================================

def test_update_specialization_invalid_uuid(
    staff_headers,
):
    response = client.patch(
        "/specializations/not-a-valid-uuid",
        headers=staff_headers,
        json={
            "name": "Invalid UUID",
        },
    )

    assert response.status_code == 422


# ============================================================
# QA-15.4.9 Update department
# ============================================================

def test_update_specialization_department(
    staff_headers,
):
    response = client.get("/specializations")

    assert response.status_code == 200

    data = response.json()

    if isinstance(data, dict):
        items = data.get("items", data.get("data", []))
    else:
        items = data

    if not items:
        pytest.skip("No specialization exists")

    specialization = items[0]

    department_id = specialization.get("department_id")

    if not department_id:
        pytest.skip("Specialization has no department_id")

    new_name = f"Department Update {uuid.uuid4().hex[:8]}"

    response = client.patch(
        f"/specializations/{specialization['id']}",
        headers=staff_headers,
        json={
            "name": new_name,
            "department_id": department_id,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == specialization["id"]
    assert data["department_id"] == department_id


# ============================================================
# QA-15.4.10 Patient forbidden
# ============================================================

def test_update_specialization_patient_forbidden(
    existing_specialization_id,
):
    pytest.skip(
        "Requires a real Patient account credential. "
        "Manual Functional Test should verify 403 Forbidden."
    )