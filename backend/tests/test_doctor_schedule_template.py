import uuid
from datetime import time

import pytest
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.enums import UserRoleEnum, WeekdayEnum
from app.core.exceptions import ConflictException, NotFoundException
from app.models.doctor import Doctor
from app.models.doctor_schedule_template import DoctorScheduleTemplate
from app.models.user import User
from app.repositories.doctor_schedule_template_repository import (
    DoctorScheduleTemplateRepository,
)
from app.schemas.doctor_schedule_template import (
    DoctorScheduleTemplateCreateRequest,
    DoctorScheduleTemplateUpdateRequest,
)
from app.services.doctor_schedule_template_service import (
    DoctorScheduleTemplateService,
)


def get_doctor(db):
    return db.scalar(
        select(Doctor)
        .order_by(Doctor.created_at.desc())
        .limit(1)
    )


def get_doctor_user(db):
    doctor = get_doctor(db)

    if doctor is None:
        return None

    return db.get(User, doctor.user_id)


def get_template(db, doctor_id=None):
    stmt = select(DoctorScheduleTemplate)

    if doctor_id is not None:
        stmt = stmt.where(
            DoctorScheduleTemplate.doctor_id == doctor_id,
        )

    return db.scalar(
        stmt.order_by(
            DoctorScheduleTemplate.created_at.desc()
        ).limit(1)
    )


def build_create_request(
    doctor_id,
    weekday=WeekdayEnum.MONDAY,
    start_time=time(9, 0),
    end_time=time(10, 0),
):
    return DoctorScheduleTemplateCreateRequest(
        doctor_id=doctor_id,
        weekday=weekday,
        start_time=start_time,
        end_time=end_time,
    )


def build_service(db):
    return DoctorScheduleTemplateService(db)


# ============================================================
# QA-11.1 CREATE SCHEDULE TEMPLATE
# ============================================================


def test_create_schedule_template_success():
    db = SessionLocal()

    created_template_id = None

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        service = build_service(db)

        request = build_create_request(
            doctor_id=doctor.id,
        )

        result = service.create_template(request)
        created_template_id = result.id

        assert result.id is not None
        assert result.doctor_id == doctor.id
        assert result.weekday == request.weekday
        assert result.start_time == request.start_time
        assert result.end_time == request.end_time
        assert result.is_active is True

    finally:
        if created_template_id is not None:
            template = db.get(
                DoctorScheduleTemplate,
                created_template_id,
            )

            if template is not None:
                db.delete(template)
                db.commit()

        db.close()


def test_create_schedule_template_doctor_not_found():
    db = SessionLocal()

    try:
        service = build_service(db)

        request = build_create_request(
            doctor_id=uuid.uuid4(),
        )

        with pytest.raises(NotFoundException):
            service.create_template(request)

    finally:
        db.rollback()
        db.close()


def test_create_schedule_template_overlap_conflict():
    db = SessionLocal()

    first_template_id = None
    second_template_id = None

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        service = build_service(db)

        first = service.create_template(
            build_create_request(
                doctor.id,
                weekday=WeekdayEnum.MONDAY,
                start_time=time(9, 0),
                end_time=time(10, 0),
            )
        )

        first_template_id = first.id

        with pytest.raises(ConflictException):
            service.create_template(
                build_create_request(
                    doctor.id,
                    weekday=WeekdayEnum.MONDAY,
                    start_time=time(9, 30),
                    end_time=time(10, 30),
                )
            )

    finally:
        if first_template_id is not None:
            template = db.get(
                DoctorScheduleTemplate,
                first_template_id,
            )

            if template is not None:
                db.delete(template)

        if second_template_id is not None:
            template = db.get(
                DoctorScheduleTemplate,
                second_template_id,
            )

            if template is not None:
                db.delete(template)

        db.commit()
        db.close()


def test_create_schedule_template_adjacent_time_allowed():
    db = SessionLocal()

    created_ids = []

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        service = build_service(db)

        first = service.create_template(
            build_create_request(
                doctor.id,
                weekday=WeekdayEnum.TUESDAY,
                start_time=time(9, 0),
                end_time=time(10, 0),
            )
        )

        created_ids.append(first.id)

        second = service.create_template(
            build_create_request(
                doctor.id,
                weekday=WeekdayEnum.TUESDAY,
                start_time=time(10, 0),
                end_time=time(11, 0),
            )
        )

        created_ids.append(second.id)

        assert second.id is not None

    finally:
        for template_id in created_ids:
            template = db.get(
                DoctorScheduleTemplate,
                template_id,
            )

            if template is not None:
                db.delete(template)

        db.commit()
        db.close()


# ============================================================
# QA-11.2 GET TEMPLATE
# ============================================================


def test_get_schedule_template_success():
    db = SessionLocal()

    created_template_id = None

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        service = build_service(db)

        created = service.create_template(
            build_create_request(
                doctor.id,
                weekday=WeekdayEnum.WEDNESDAY,
            )
        )

        created_template_id = created.id

        result = service.get_template(created.id)

        assert result.id == created.id
        assert result.doctor_id == doctor.id
        assert result.weekday == created.weekday

    finally:
        if created_template_id is not None:
            template = db.get(
                DoctorScheduleTemplate,
                created_template_id,
            )

            if template is not None:
                db.delete(template)

            db.commit()

        db.close()


def test_get_schedule_template_not_found():
    db = SessionLocal()

    try:
        service = build_service(db)

        with pytest.raises(NotFoundException):
            service.get_template(uuid.uuid4())

    finally:
        db.rollback()
        db.close()


# ============================================================
# QA-11.3 LIST BY DOCTOR
# ============================================================


def test_list_schedule_templates_by_doctor_success():
    db = SessionLocal()

    created_ids = []

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        service = build_service(db)

        first = service.create_template(
            build_create_request(
                doctor.id,
                weekday=WeekdayEnum.THURSDAY,
                start_time=time(9, 0),
                end_time=time(10, 0),
            )
        )

        second = service.create_template(
            build_create_request(
                doctor.id,
                weekday=WeekdayEnum.THURSDAY,
                start_time=time(11, 0),
                end_time=time(12, 0),
            )
        )

        created_ids.extend(
            [first.id, second.id]
        )

        result = service.list_by_doctor(
            doctor.id,
        )

        assert isinstance(result, list)
        assert all(
            item.doctor_id == doctor.id
            for item in result
        )

        ids = {item.id for item in result}

        assert first.id in ids
        assert second.id in ids

    finally:
        for template_id in created_ids:
            template = db.get(
                DoctorScheduleTemplate,
                template_id,
            )

            if template is not None:
                db.delete(template)

        db.commit()
        db.close()


def test_list_schedule_templates_by_doctor_not_found():
    db = SessionLocal()

    try:
        service = build_service(db)

        with pytest.raises(NotFoundException):
            service.list_by_doctor(
                uuid.uuid4(),
            )

    finally:
        db.rollback()
        db.close()


def test_list_schedule_templates_ordered():
    db = SessionLocal()

    created_ids = []

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        service = build_service(db)

        first = service.create_template(
            build_create_request(
                doctor.id,
                weekday=WeekdayEnum.FRIDAY,
                start_time=time(13, 0),
                end_time=time(14, 0),
            )
        )

        second = service.create_template(
            build_create_request(
                doctor.id,
                weekday=WeekdayEnum.MONDAY,
                start_time=time(9, 0),
                end_time=time(10, 0),
            )
        )

        created_ids.extend(
            [first.id, second.id]
        )

        result = service.list_by_doctor(
            doctor.id,
        )

        positions = [
            item.id
            for item in result
            if item.id in created_ids
        ]

        assert positions.index(second.id) < positions.index(first.id)

    finally:
        for template_id in created_ids:
            template = db.get(
                DoctorScheduleTemplate,
                template_id,
            )

            if template is not None:
                db.delete(template)

        db.commit()
        db.close()


# ============================================================
# QA-11.4 MY SCHEDULE
# ============================================================


def test_get_my_schedule_success():
    db = SessionLocal()

    try:
        doctor_user = get_doctor_user(db)

        if doctor_user is None:
            pytest.skip("No doctor user found.")

        service = build_service(db)

        result = service.get_my_schedule(
            doctor_user,
        )

        assert isinstance(result, list)

        for item in result:
            assert item.doctor_id == get_doctor(db).id

    finally:
        db.rollback()
        db.close()


def test_get_my_schedule_non_doctor_forbidden():
    db = SessionLocal()

    try:
        user = db.scalar(
            select(User)
            .where(
                User.role != UserRoleEnum.DOCTOR,
            )
            .limit(1)
        )

        if user is None:
            pytest.skip("No non-doctor user found.")

        service = build_service(db)

        with pytest.raises(ConflictException):
            service.get_my_schedule(user)

    finally:
        db.rollback()
        db.close()


# ============================================================
# QA-11.5 UPDATE
# ============================================================


def test_update_schedule_template_success():
    db = SessionLocal()

    created_template_id = None

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        service = build_service(db)

        created = service.create_template(
            build_create_request(
                doctor.id,
                weekday=WeekdayEnum.SATURDAY,
                start_time=time(9, 0),
                end_time=time(10, 0),
            )
        )

        created_template_id = created.id

        result = service.update_template(
            created.id,
            DoctorScheduleTemplateUpdateRequest(
                start_time=time(10, 0),
                end_time=time(11, 0),
            ),
        )

        assert result.id == created.id
        assert result.start_time == time(10, 0)
        assert result.end_time == time(11, 0)

    finally:
        if created_template_id is not None:
            template = db.get(
                DoctorScheduleTemplate,
                created_template_id,
            )

            if template is not None:
                db.delete(template)

            db.commit()

        db.close()


def test_update_schedule_template_not_found():
    db = SessionLocal()

    try:
        service = build_service(db)

        with pytest.raises(NotFoundException):
            service.update_template(
                uuid.uuid4(),
                DoctorScheduleTemplateUpdateRequest(
                    is_active=False,
                ),
            )

    finally:
        db.rollback()
        db.close()


def test_update_schedule_template_overlap_conflict():
    db = SessionLocal()

    created_ids = []

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        service = build_service(db)

        first = service.create_template(
            build_create_request(
                doctor.id,
                weekday=WeekdayEnum.SUNDAY,
                start_time=time(9, 0),
                end_time=time(10, 0),
            )
        )

        second = service.create_template(
            build_create_request(
                doctor.id,
                weekday=WeekdayEnum.SUNDAY,
                start_time=time(11, 0),
                end_time=time(12, 0),
            )
        )

        created_ids.extend(
            [first.id, second.id]
        )

        with pytest.raises(ConflictException):
            service.update_template(
                second.id,
                DoctorScheduleTemplateUpdateRequest(
                    start_time=time(9, 30),
                    end_time=time(10, 30),
                ),
            )

    finally:
        for template_id in created_ids:
            template = db.get(
                DoctorScheduleTemplate,
                template_id,
            )

            if template is not None:
                db.delete(template)

        db.commit()
        db.close()


def test_update_schedule_template_self_exclusion():
    db = SessionLocal()

    created_template_id = None

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        service = build_service(db)

        created = service.create_template(
            build_create_request(
                doctor.id,
                weekday=WeekdayEnum.MONDAY,
                start_time=time(14, 0),
                end_time=time(15, 0),
            )
        )

        created_template_id = created.id

        result = service.update_template(
            created.id,
            DoctorScheduleTemplateUpdateRequest(
                start_time=time(14, 0),
                end_time=time(15, 0),
            ),
        )

        assert result.id == created.id

    finally:
        if created_template_id is not None:
            template = db.get(
                DoctorScheduleTemplate,
                created_template_id,
            )

            if template is not None:
                db.delete(template)

            db.commit()

        db.close()


def test_update_schedule_template_is_active():
    db = SessionLocal()

    created_template_id = None

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        service = build_service(db)

        created = service.create_template(
            build_create_request(
                doctor.id,
                weekday=WeekdayEnum.TUESDAY,
                start_time=time(14, 0),
                end_time=time(15, 0),
            )
        )

        created_template_id = created.id

        result = service.update_template(
            created.id,
            DoctorScheduleTemplateUpdateRequest(
                is_active=False,
            ),
        )

        assert result.id == created.id
        assert result.is_active is False

    finally:
        if created_template_id is not None:
            template = db.get(
                DoctorScheduleTemplate,
                created_template_id,
            )

            if template is not None:
                db.delete(template)

            db.commit()

        db.close()


# ============================================================
# QA-11.6 DELETE
# ============================================================


def test_delete_schedule_template_success():
    db = SessionLocal()

    created_template_id = None

    try:
        doctor = get_doctor(db)

        if doctor is None:
            pytest.skip("No doctor found.")

        service = build_service(db)

        created = service.create_template(
            build_create_request(
                doctor.id,
                weekday=WeekdayEnum.WEDNESDAY,
                start_time=time(14, 0),
                end_time=time(15, 0),
            )
        )

        created_template_id = created.id

        result = service.delete_template(
            created.id,
        )

        assert result is None
        assert (
            db.get(
                DoctorScheduleTemplate,
                created.id,
            )
            is None
        )

        created_template_id = None

    finally:
        if created_template_id is not None:
            template = db.get(
                DoctorScheduleTemplate,
                created_template_id,
            )

            if template is not None:
                db.delete(template)

            db.commit()

        db.close()


def test_delete_schedule_template_not_found():
    db = SessionLocal()

    try:
        service = build_service(db)

        with pytest.raises(NotFoundException):
            service.delete_template(
                uuid.uuid4(),
            )

    finally:
        db.rollback()
        db.close()


# ============================================================
# QA-11.7 VALIDATION
# ============================================================


@pytest.mark.parametrize(
    "start_time,end_time",
    [
        (time(10, 0), time(10, 0)),
        (time(11, 0), time(10, 0)),
    ],
)
def test_create_schedule_template_invalid_time_range(
    start_time,
    end_time,
):
    doctor_id = uuid.uuid4()

    with pytest.raises(ValueError):
        DoctorScheduleTemplateCreateRequest(
            doctor_id=doctor_id,
            weekday=WeekdayEnum.MONDAY,
            start_time=start_time,
            end_time=end_time,
        )


def test_update_schedule_template_invalid_time_range():
    with pytest.raises(ValueError):
        DoctorScheduleTemplateUpdateRequest(
            start_time=time(11, 0),
            end_time=time(10, 0),
        )


def test_update_schedule_template_partial_time_update():
    request = DoctorScheduleTemplateUpdateRequest(
        start_time=time(13, 0),
    )

    assert request.start_time == time(13, 0)
    assert request.end_time is None
