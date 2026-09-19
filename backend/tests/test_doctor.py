import uuid

import pytest
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.enums import (
    DoctorPrefaceEnum,
    DoctorStatusEnum,
    UserRoleEnum,
)
from app.core.exceptions import (
    DepartmentNotFoundException,
    DoctorEmailAlreadyExistsException,
    DoctorLicenseAlreadyExistsException,
    DoctorNotFoundException,
    DoctorPhoneNumberAlreadyExistsException,
    InvalidCredentialsException,
    SpecializationNotFoundException,
    UsernameAlreadyExistsException,
)
from app.models.department import Department
from app.models.doctor import Doctor
from app.models.doctor_specialization import DoctorSpecialization
from app.models.specialization import Specialization
from app.models.user import User
from app.schemas.doctor import (
    DoctorCreateRequest,
    DoctorDeactivateRequest,
    DoctorUpdateRequest,
)
from app.services.doctor_service import DoctorService


def get_staff(db):
    return db.scalar(
        select(User)
        .where(
            User.role == UserRoleEnum.HOSPITAL_STAFF,
        )
        .limit(1)
    )


def get_department(db):
    return db.scalar(
        select(Department)
        .limit(1)
    )


def get_specializations(db, minimum=1):
    return list(
        db.scalars(
            select(Specialization)
            .limit(minimum)
        ).all()
    )


def get_doctor(db, status=None):
    stmt = select(Doctor)

    if status is not None:
        stmt = stmt.where(
            Doctor.status == status,
        )

    return db.scalar(
        stmt.order_by(
            Doctor.created_at.desc()
        ).limit(1)
    )


def build_unique_suffix():
    return uuid.uuid4().hex[:8]


def build_create_request(
    db,
    employee_id=None,
    email=None,
    phone_number=None,
    license_number=None,
):
    department = get_department(db)

    if department is None:
        pytest.skip("No department found.")

    specializations = get_specializations(db, 1)

    if len(specializations) < 1:
        pytest.skip("No specialization found.")

    suffix = build_unique_suffix()
    numeric_suffix = str(int(suffix, 16))[-8:].zfill(8)

    return DoctorCreateRequest(
        employee_id=employee_id
        or f"TESTDOC{suffix}",
        password="TestPassword123!",
        preface=DoctorPrefaceEnum.MR_DOCTOR,
        first_name="Test",
        last_name="Doctor",
        license_number=license_number
        or f"ว.{numeric_suffix}",
        phone_number=phone_number
        or f"08{numeric_suffix}",
        email=email
        or f"testdoctor{suffix}@example.com",
        department_id=department.id,
        specialization_ids=[
            specializations[0].id,
        ],
    )


# ============================================================
# QA-09.1 GET DOCTORS
# ============================================================


def test_get_doctors_default_active():
    db = SessionLocal()

    try:
        service = DoctorService(db)

        doctors = service.get_doctors()

        assert isinstance(doctors, list)

        for doctor in doctors:
            assert doctor.status == DoctorStatusEnum.ACTIVE

    finally:
        db.rollback()
        db.close()


def test_get_doctors_filter_by_department():
    db = SessionLocal()

    try:
        doctor = get_doctor(
            db,
            DoctorStatusEnum.ACTIVE,
        )

        if doctor is None:
            pytest.skip("No active doctor found.")

        service = DoctorService(db)

        doctors = service.get_doctors(
            department_id=doctor.department_id,
        )

        assert isinstance(doctors, list)

        for item in doctors:
            assert item.department_id == doctor.department_id

    finally:
        db.rollback()
        db.close()


@pytest.mark.parametrize(
    "status",
    [
        DoctorStatusEnum.ACTIVE,
        DoctorStatusEnum.INACTIVE,
    ],
)
def test_get_doctors_filter_by_status(status):
    db = SessionLocal()

    try:
        service = DoctorService(db)

        doctors = service.get_doctors(
            status=status,
        )

        assert isinstance(doctors, list)

        for doctor in doctors:
            assert doctor.status == status

    finally:
        db.rollback()
        db.close()


def test_get_doctors_search():
    db = SessionLocal()

    try:
        doctor = get_doctor(
            db,
            DoctorStatusEnum.ACTIVE,
        )

        if doctor is None:
            pytest.skip("No active doctor found.")

        service = DoctorService(db)

        doctors = service.get_doctors(
            search=doctor.first_name,
        )

        assert isinstance(doctors, list)

        assert any(
            item.id == doctor.id
            for item in doctors
        )

    finally:
        db.rollback()
        db.close()


def test_get_doctors_search_strips_whitespace():
    db = SessionLocal()

    try:
        doctor = get_doctor(
            db,
            DoctorStatusEnum.ACTIVE,
        )

        if doctor is None:
            pytest.skip("No active doctor found.")

        service = DoctorService(db)

        doctors = service.get_doctors(
            search=f"  {doctor.first_name}  ",
        )

        assert any(
            item.id == doctor.id
            for item in doctors
        )

    finally:
        db.rollback()
        db.close()


# ============================================================
# QA-09.2 GET DOCTOR BY ID
# ============================================================


def test_get_doctor_by_id_success():
    db = SessionLocal()

    try:
        doctor = get_doctor(
            db,
            DoctorStatusEnum.ACTIVE,
        )

        if doctor is None:
            pytest.skip("No active doctor found.")

        service = DoctorService(db)

        result = service.get_doctor_by_id(
            doctor.id,
        )

        assert result.id == doctor.id
        assert result.status == DoctorStatusEnum.ACTIVE
        assert result.department is not None
        assert result.specializations is not None

    finally:
        db.rollback()
        db.close()


def test_get_doctor_by_id_not_found():
    db = SessionLocal()

    try:
        service = DoctorService(db)

        with pytest.raises(
            DoctorNotFoundException
        ):
            service.get_doctor_by_id(
                uuid.uuid4(),
            )

    finally:
        db.rollback()
        db.close()


def test_get_doctor_by_id_inactive_not_found():
    db = SessionLocal()

    try:
        doctor = get_doctor(
            db,
            DoctorStatusEnum.INACTIVE,
        )

        if doctor is None:
            pytest.skip("No inactive doctor found.")

        service = DoctorService(db)

        with pytest.raises(
            DoctorNotFoundException
        ):
            service.get_doctor_by_id(
                doctor.id,
            )

    finally:
        db.rollback()
        db.close()


# ============================================================
# QA-09.3 CREATE DOCTOR
# ============================================================


def test_create_doctor_success():
    db = SessionLocal()

    created_doctor_id = None

    try:
        request = build_create_request(db)

        service = DoctorService(db)

        result = service.create_doctor(request)

        created_doctor_id = result.id

        assert result.id is not None
        assert result.first_name == request.first_name
        assert result.last_name == request.last_name
        assert result.email == request.email
        assert result.phone_number == request.phone_number
        assert result.license_number == request.license_number
        assert result.status == DoctorStatusEnum.ACTIVE
        assert result.department is not None
        assert len(result.specializations) == 1

    finally:
        if created_doctor_id is not None:
            doctor = db.get(
                Doctor,
                created_doctor_id,
            )

            if doctor is not None:
                user = db.get(
                    User,
                    doctor.user_id,
                )

            db.query(DoctorSpecialization).filter(
                DoctorSpecialization.doctor_id == doctor.id
            ).delete(
                synchronize_session=False
            )

            db.delete(doctor)

            if user is not None:
              db.delete(user)

            db.commit()
            db.close()


def test_create_doctor_duplicate_employee_id():
    db = SessionLocal()

    try:
        existing_user = db.scalar(
            select(User)
            .where(
                User.role == UserRoleEnum.DOCTOR,
            )
            .limit(1)
        )

        if existing_user is None:
            pytest.skip("No existing doctor user found.")

        request = build_create_request(
            db,
            employee_id=existing_user.username,
        )

        service = DoctorService(db)

        with pytest.raises(
            UsernameAlreadyExistsException
        ):
            service.create_doctor(request)

    finally:
        db.rollback()
        db.close()


def test_create_doctor_duplicate_email():
    db = SessionLocal()

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        request = build_create_request(
            db,
            email=doctor.email,
        )

        service = DoctorService(db)

        with pytest.raises(
            DoctorEmailAlreadyExistsException
        ):
            service.create_doctor(request)

    finally:
        db.rollback()
        db.close()


def test_create_doctor_duplicate_phone():
    db = SessionLocal()

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        request = build_create_request(
            db,
            phone_number=doctor.phone_number,
        )

        service = DoctorService(db)

        with pytest.raises(
            DoctorPhoneNumberAlreadyExistsException
        ):
            service.create_doctor(request)

    finally:
        db.rollback()
        db.close()


def test_create_doctor_duplicate_license():
    db = SessionLocal()

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        request = build_create_request(
            db,
            license_number=doctor.license_number,
        )

        service = DoctorService(db)

        with pytest.raises(
            DoctorLicenseAlreadyExistsException
        ):
            service.create_doctor(request)

    finally:
        db.rollback()
        db.close()


def test_create_doctor_department_not_found():
    db = SessionLocal()

    try:
        specializations = get_specializations(db, 1)

        if not specializations:
            pytest.skip("No specialization found.")

        suffix = build_unique_suffix()
        numeric_suffix = str(int(suffix, 16))[-8:].zfill(8)

        request = DoctorCreateRequest(
            employee_id=f"TESTDOC{suffix}",
            password="TestPassword123!",
            preface=DoctorPrefaceEnum.MR_DOCTOR,
            first_name="Test",
            last_name="Doctor",
            license_number=f"ว.{numeric_suffix}",
            phone_number=f"08{numeric_suffix}",
            email=f"testdoctor{suffix}@example.com",
            department_id=uuid.uuid4(),
            specialization_ids=[
                specializations[0].id,
            ],
        )

        service = DoctorService(db)

        with pytest.raises(
            DepartmentNotFoundException
        ):
            service.create_doctor(request)

    finally:
        db.rollback()
        db.close()


def test_create_doctor_specialization_not_found():
    db = SessionLocal()

    try:
        department = get_department(db)

        if department is None:
            pytest.skip("No department found.")

        suffix = build_unique_suffix()
        numeric_suffix = str(int(suffix, 16))[-8:].zfill(8)

        request = DoctorCreateRequest(
            employee_id=f"TESTDOC{suffix}",
            password="TestPassword123!",
            preface=DoctorPrefaceEnum.MR_DOCTOR,
            first_name="Test",
            last_name="Doctor",
            license_number=f"ว.{numeric_suffix}",
            phone_number=f"08{numeric_suffix}",
            email=f"testdoctor{suffix}@example.com",
            department_id=department.id,
            specialization_ids=[
                uuid.uuid4(),
            ],
        )

        service = DoctorService(db)

        with pytest.raises(
            SpecializationNotFoundException
        ):
            service.create_doctor(request)

    finally:
        db.rollback()
        db.close()


# ============================================================
# QA-09.4 UPDATE DOCTOR
# ============================================================


def test_update_doctor_success():
    db = SessionLocal()

    try:
        doctor = get_doctor(
            db,
            DoctorStatusEnum.ACTIVE,
        )

        if doctor is None:
            pytest.skip("No active doctor found.")

        original_first_name = doctor.first_name

        service = DoctorService(db)

        request = DoctorUpdateRequest(
            first_name="Updated",
        )

        result = service.update_doctor(
            doctor.id,
            request,
        )

        assert result.id == doctor.id
        assert result.first_name == "Updated"

        # คืนค่าข้อมูลเดิม
        doctor.first_name = original_first_name
        db.commit()

    finally:
        db.rollback()
        db.close()


def test_update_doctor_not_found():
    db = SessionLocal()

    try:
        service = DoctorService(db)

        request = DoctorUpdateRequest(
            first_name="Updated",
        )

        with pytest.raises(
            DoctorNotFoundException
        ):
            service.update_doctor(
                uuid.uuid4(),
                request,
            )

    finally:
        db.rollback()
        db.close()


def test_update_doctor_duplicate_email():
    db = SessionLocal()

    try:
        doctors = list(
            db.scalars(
                select(Doctor)
                .limit(2)
            ).all()
        )

        if len(doctors) < 2:
            pytest.skip("Need at least two doctors.")

        target = doctors[0]
        other = doctors[1]

        service = DoctorService(db)

        request = DoctorUpdateRequest(
            email=other.email,
        )

        with pytest.raises(
            DoctorEmailAlreadyExistsException
        ):
            service.update_doctor(
                target.id,
                request,
            )

    finally:
        db.rollback()
        db.close()


def test_update_doctor_duplicate_phone():
    db = SessionLocal()

    try:
        doctors = list(
            db.scalars(
                select(Doctor)
                .limit(2)
            ).all()
        )

        if len(doctors) < 2:
            pytest.skip("Need at least two doctors.")

        target = doctors[0]
        other = doctors[1]

        service = DoctorService(db)

        request = DoctorUpdateRequest(
            phone_number=other.phone_number,
        )

        with pytest.raises(
            DoctorPhoneNumberAlreadyExistsException
        ):
            service.update_doctor(
                target.id,
                request,
            )

    finally:
        db.rollback()
        db.close()


def test_update_doctor_department_not_found():
    db = SessionLocal()

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        service = DoctorService(db)

        request = DoctorUpdateRequest(
            department_id=uuid.uuid4(),
        )

        with pytest.raises(
            DepartmentNotFoundException
        ):
            service.update_doctor(
                doctor.id,
                request,
            )

    finally:
        db.rollback()
        db.close()


def test_update_doctor_specialization_not_found():
    db = SessionLocal()

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        service = DoctorService(db)

        request = DoctorUpdateRequest(
            specialization_ids=[
                uuid.uuid4(),
            ],
        )

        with pytest.raises(
            SpecializationNotFoundException
        ):
            service.update_doctor(
                doctor.id,
                request,
            )

    finally:
        db.rollback()
        db.close()


def test_update_doctor_specializations_success():
    db = SessionLocal()

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        specializations = get_specializations(db, 1)

        if not specializations:
            pytest.skip("No specialization found.")

        service = DoctorService(db)

        original_ids = [
            item.id
            for item in doctor.specializations
        ]

        request = DoctorUpdateRequest(
            specialization_ids=[
                specializations[0].id,
            ],
        )

        result = service.update_doctor(
            doctor.id,
            request,
        )

        assert result.id == doctor.id

        db.refresh(doctor)

        assert len(doctor.specializations) == 1
        assert (
            doctor.specializations[0].id
            == specializations[0].id
        )

        # คืนค่าเดิมถ้ามีข้อมูลเดิม
        if original_ids:
            doctor.specializations = list(
                db.scalars(
                    select(Specialization)
                    .where(
                        Specialization.id.in_(
                            original_ids
                        )
                    )
                ).all()
            )
            db.commit()

    finally:
        db.rollback()
        db.close()


# ============================================================
# QA-09.5 DEACTIVATE DOCTOR
# ============================================================


def test_delete_doctor_success():
    db = SessionLocal()

    created_doctor_id = None

    try:
        request = build_create_request(db)

        service = DoctorService(db)

        created = service.create_doctor(
            request
        )

        created_doctor_id = created.id

        staff = get_staff(db)

        if staff is None:
            pytest.skip(
                "No hospital staff user found."
            )

        deactivate_request = DoctorDeactivateRequest(
            password="TestPassword123!",
        )

        # ใช้ password จริงของ Staff
        # เพื่อให้การทดสอบไม่พึ่ง Mock
        from app.utils.security import hash_password

        original_password = staff.password
        staff.password = hash_password(
            "TestPassword123!"
        )
        db.commit()

        result = service.delete_doctor(
            doctor_id=created.id,
            request=deactivate_request,
            current_user=staff,
        )

        assert result.id == created.id
        assert result.status == DoctorStatusEnum.INACTIVE

        doctor = db.get(
              Doctor,
              created.id,
          )

        assert doctor is not None
        assert doctor.status == (
              DoctorStatusEnum.INACTIVE
          )

    finally:
        # Doctor ถูก deactivate แล้ว จึงไม่ลบผ่าน service
        # เพราะ delete_doctor เปลี่ยนสถานะเป็น INACTIVE
        if created_doctor_id is not None:
            doctor = db.get(
                Doctor,
                created_doctor_id,
            )

            if doctor is not None:
                user = db.get(
                    User,
                    doctor.user_id,
                )

                # ลบความสัมพันธ์ก่อน
                db.query(
                    DoctorSpecialization
                ).filter(
                    DoctorSpecialization.doctor_id
                    == doctor.id
                ).delete(
                    synchronize_session=False
                )

                db.delete(doctor)

                if user is not None:
                    db.delete(user)

                db.commit()

        db.close()


def test_delete_doctor_wrong_password():
    db = SessionLocal()

    try:
        doctor = get_doctor(
            db,
            DoctorStatusEnum.ACTIVE,
        )

        staff = get_staff(db)

        if doctor is None:
            pytest.skip("No active doctor found.")

        if staff is None:
            pytest.skip(
                "No hospital staff user found."
            )

        service = DoctorService(db)

        request = DoctorDeactivateRequest(
            password="DefinitelyWrongPassword123!",
        )

        with pytest.raises(
            InvalidCredentialsException
        ):
            service.delete_doctor(
                doctor.id,
                request,
                staff,
            )

    finally:
        db.rollback()
        db.close()


def test_delete_doctor_not_found():
    db = SessionLocal()

    try:
        staff = get_staff(db)

        if staff is None:
            pytest.skip(
                "No hospital staff user found."
            )

        service = DoctorService(db)

        request = DoctorDeactivateRequest(
            password="anything",
        )

        with pytest.raises(
            DoctorNotFoundException
        ):
            service.delete_doctor(
                uuid.uuid4(),
                request,
                staff,
            )

    finally:
        db.rollback()
        db.close()


def test_delete_doctor_invalid_current_user():
    db = SessionLocal()

    try:
        doctor = get_doctor(
            db,
            DoctorStatusEnum.ACTIVE,
        )

        if doctor is None:
            pytest.skip("No active doctor found.")

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

        service = DoctorService(db)

        request = DoctorDeactivateRequest(
            password="anything",
        )

        with pytest.raises(
            InvalidCredentialsException
        ):
            service.delete_doctor(
                doctor.id,
                request,
                fake_user,
            )

    finally:
        db.rollback()
        db.close()