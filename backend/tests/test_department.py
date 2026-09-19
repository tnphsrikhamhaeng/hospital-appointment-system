import uuid

import pytest
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.enums import DepartmentStatusEnum, UserRoleEnum
from app.core.exceptions import (
    DepartmentAlreadyExistsException,
    DepartmentAlreadyInactiveException,
    DepartmentNotFoundException,
    InvalidCredentialsException,
)
from app.models.department import Department
from app.models.user import User
from app.schemas.department import (
    DepartmentCreateRequest,
    DepartmentDeactivateRequest,
    DepartmentUpdateRequest,
)
from app.services.department_service import DepartmentService
from app.utils.security import hash_password


def get_staff(db):
    return db.scalar(
        select(User)
        .where(
            User.role == UserRoleEnum.HOSPITAL_STAFF,
        )
        .limit(1)
    )


def get_department(db, status=None):
    stmt = select(Department)

    if status is not None:
        stmt = stmt.where(
            Department.status == status,
        )

    return db.scalar(
        stmt.order_by(
            Department.created_at.desc()
        ).limit(1)
    )


def build_unique_suffix():
    return uuid.uuid4().hex[:8]


def build_create_request(
    name=None,
    description="Test department",
    image_url=None,
    slot_duration_minutes=30,
):
    suffix = build_unique_suffix()

    return DepartmentCreateRequest(
        name=name or f"Test Department {suffix}",
        description=description,
        image_url=image_url,
        slot_duration_minutes=slot_duration_minutes,
    )


# ============================================================
# QA-10.1 CREATE DEPARTMENT
# ============================================================


def test_create_department_success():
    db = SessionLocal()

    created_department_id = None

    try:
        request = build_create_request()
        service = DepartmentService(
            repository=__import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db=db,
        )

        result = service.create(request)
        created_department_id = result.id

        assert result.id is not None
        assert result.name == request.name
        assert result.description == request.description
        assert result.image_url == request.image_url
        assert result.slot_duration_minutes == request.slot_duration_minutes
        assert result.status == DepartmentStatusEnum.ACTIVE

    finally:
        if created_department_id is not None:
            department = db.get(
                Department,
                created_department_id,
            )

            if department is not None:
                db.delete(department)
                db.commit()

        db.close()


def test_create_department_duplicate_name():
    db = SessionLocal()

    try:
        department = get_department(
          db,
          DepartmentStatusEnum.ACTIVE,
      )

        if department is None:
            pytest.skip("No department found.")

        request = build_create_request(
            name=department.name,
        )

        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        with pytest.raises(
            DepartmentAlreadyExistsException
        ):
            service.create(request)

    finally:
        db.rollback()
        db.close()


# ============================================================
# QA-10.2 GET DEPARTMENT
# ============================================================


def test_get_department_success():
    db = SessionLocal()

    try:
        department = get_department(db)

        if department is None:
            pytest.skip("No department found.")

        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        result = service.get(department.id)

        assert result.id == department.id
        assert result.name == department.name
        assert result.status == department.status

    finally:
        db.rollback()
        db.close()


def test_get_department_not_found():
    db = SessionLocal()

    try:
        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        with pytest.raises(
            DepartmentNotFoundException
        ):
            service.get(uuid.uuid4())

    finally:
        db.rollback()
        db.close()


# ============================================================
# QA-10.3 LIST DEPARTMENT
# ============================================================


def test_list_departments_default_active():
    db = SessionLocal()

    try:
        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        departments = service.list()

        assert isinstance(departments, list)

        for department in departments:
            assert department.status == DepartmentStatusEnum.ACTIVE

    finally:
        db.rollback()
        db.close()


@pytest.mark.parametrize(
    "status",
    [
        DepartmentStatusEnum.ACTIVE,
        DepartmentStatusEnum.INACTIVE,
    ],
)
def test_list_departments_filter_by_status(status):
    db = SessionLocal()

    try:
        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        departments = service.list(
            status=status,
        )

        assert isinstance(departments, list)

        for department in departments:
            assert department.status == status

    finally:
        db.rollback()
        db.close()


def test_list_departments_search_name():
    db = SessionLocal()

    try:
        department = get_department(
            db,
            DepartmentStatusEnum.ACTIVE,
        )

        if department is None:
            pytest.skip("No active department found.")

        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        departments = service.list(
            search=department.name,
        )

        assert any(
            item.id == department.id
            for item in departments
        )

    finally:
        db.rollback()
        db.close()


def test_list_departments_search_description():
    db = SessionLocal()

    try:
        department = db.scalar(
            select(Department)
            .where(
                Department.description.is_not(None),
            )
            .limit(1)
        )

        if department is None:
            pytest.skip("No department with description found.")

        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        search_value = department.description.split()[0]

        departments = service.list(
            search=search_value,
        )

        assert any(
            item.id == department.id
            for item in departments
        )

    finally:
        db.rollback()
        db.close()


# ============================================================
# QA-10.4 UPDATE DEPARTMENT
# ============================================================


def test_update_department_success():
    db = SessionLocal()

    try:
        department = get_department(
            db,
            DepartmentStatusEnum.ACTIVE,
        )

        if department is None:
            pytest.skip("No active department found.")

        original_description = department.description

        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        request = DepartmentUpdateRequest(
            description=f"Updated {build_unique_suffix()}",
        )

        result = service.update(
            department.id,
            request,
        )

        assert result.id == department.id
        assert result.description == request.description

        department.description = original_description
        db.commit()

    finally:
        db.rollback()
        db.close()


def test_update_department_name_success():
    db = SessionLocal()

    try:
        department = get_department(
            db,
            DepartmentStatusEnum.ACTIVE,
        )

        if department is None:
            pytest.skip("No active department found.")

        original_name = department.name
        new_name = f"Updated Department {build_unique_suffix()}"

        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        result = service.update(
            department.id,
            DepartmentUpdateRequest(
                name=new_name,
            ),
        )

        assert result.id == department.id
        assert result.name == new_name

        department.name = original_name
        db.commit()

    finally:
        db.rollback()
        db.close()


def test_update_department_not_found():
    db = SessionLocal()

    try:
        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        with pytest.raises(
            DepartmentNotFoundException
        ):
            service.update(
                uuid.uuid4(),
                DepartmentUpdateRequest(
                    description="Updated",
                ),
            )

    finally:
        db.rollback()
        db.close()


def test_update_department_duplicate_name():
    db = SessionLocal()

    try:
        departments = list(
            db.scalars(
                select(Department)
                .where(
                    Department.status
                    == DepartmentStatusEnum.ACTIVE,
                )
                .limit(2)
            ).all()
        )

        if len(departments) < 2:
            pytest.skip("Need at least two active departments.")

        target = departments[0]
        other = departments[1]

        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        with pytest.raises(
            DepartmentAlreadyExistsException
        ):
            service.update(
                target.id,
                DepartmentUpdateRequest(
                    name=other.name,
                ),
            )

    finally:
        db.rollback()
        db.close()


# ============================================================
# QA-10.5 DEACTIVATE DEPARTMENT
# ============================================================


def test_delete_department_success():
    db = SessionLocal()

    created_department_id = None
    original_password = None

    try:
        staff = get_staff(db)

        if staff is None:
            pytest.skip("No hospital staff user found.")

        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        request = build_create_request()
        created = service.create(request)
        created_department_id = created.id

        deactivate_request = DepartmentDeactivateRequest(
            password="TestPassword123!",
        )

        original_password = staff.password
        staff.password = hash_password(
            "TestPassword123!"
        )
        db.commit()

        result = service.delete(
            department_id=created.id,
            request=deactivate_request,
            current_user=staff,
        )

        assert result.id == created.id
        assert result.status == DepartmentStatusEnum.INACTIVE

        department = db.get(
            Department,
            created.id,
        )

        assert department is not None
        assert department.status == DepartmentStatusEnum.INACTIVE

    finally:
        if original_password is not None:
            staff = get_staff(db)

            if staff is not None:
                staff.password = original_password

        if created_department_id is not None:
            department = db.get(
                Department,
                created_department_id,
            )

            if department is not None:
                db.delete(department)

        db.commit()
        db.close()


def test_delete_department_wrong_password():
    db = SessionLocal()

    try:
        department = get_department(
            db,
            DepartmentStatusEnum.ACTIVE,
        )
        staff = get_staff(db)

        if department is None:
            pytest.skip("No active department found.")

        if staff is None:
            pytest.skip("No hospital staff user found.")

        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        request = DepartmentDeactivateRequest(
            password="DefinitelyWrongPassword123!",
        )

        with pytest.raises(
            InvalidCredentialsException
        ):
            service.delete(
                department.id,
                request,
                staff,
            )

    finally:
        db.rollback()
        db.close()


def test_delete_department_not_found():
    db = SessionLocal()

    try:
        staff = get_staff(db)

        if staff is None:
            pytest.skip("No hospital staff user found.")

        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        request = DepartmentDeactivateRequest(
            password="anything",
        )

        with pytest.raises(
            DepartmentNotFoundException
        ):
            service.delete(
                uuid.uuid4(),
                request,
                staff,
            )

    finally:
        db.rollback()
        db.close()


def test_delete_department_already_inactive():
    db = SessionLocal()

    try:
        department = get_department(
            db,
            DepartmentStatusEnum.INACTIVE,
        )
        staff = get_staff(db)

        if department is None:
            pytest.skip("No inactive department found.")

        if staff is None:
            pytest.skip("No hospital staff user found.")

        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        request = DepartmentDeactivateRequest(
            password="anything",
        )

        with pytest.raises(
            DepartmentAlreadyInactiveException
        ):
            service.delete(
                department.id,
                request,
                staff,
            )

    finally:
        db.rollback()
        db.close()


def test_delete_department_invalid_current_user():
    db = SessionLocal()

    try:
        department = get_department(
            db,
            DepartmentStatusEnum.ACTIVE,
        )

        if department is None:
            pytest.skip("No active department found.")

        fake_user = User(
            id=uuid.uuid4(),
            username=f"fake{build_unique_suffix()}",
            first_name="Fake",
            last_name="User",
            phone_number=f"09{build_unique_suffix()[:8]}",
            email=f"fake{build_unique_suffix()}@example.com",
            password="invalid",
            role=UserRoleEnum.HOSPITAL_STAFF,
        )

        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        request = DepartmentDeactivateRequest(
            password="anything",
        )

        with pytest.raises(
            InvalidCredentialsException
        ):
            service.delete(
                department.id,
                request,
                fake_user,
            )

    finally:
        db.rollback()
        db.close()


# ============================================================
# QA-10.6 VALIDATION / EDGE CASES
# ============================================================


@pytest.mark.parametrize(
    "slot_duration_minutes",
    [5, 120],
)
def test_create_department_slot_duration_boundary(
    slot_duration_minutes,
):
    db = SessionLocal()

    created_department_id = None

    try:
        request = build_create_request(
            slot_duration_minutes=slot_duration_minutes,
        )

        service = DepartmentService(
            __import__(
                "app.repositories.department_repository",
                fromlist=["DepartmentRepository"],
            ).DepartmentRepository(db),
            db,
        )

        result = service.create(request)
        created_department_id = result.id

        assert (
            result.slot_duration_minutes
            == slot_duration_minutes
        )

    finally:
        if created_department_id is not None:
            department = db.get(
                Department,
                created_department_id,
            )

            if department is not None:
                db.delete(department)

            db.commit()

        db.close()
