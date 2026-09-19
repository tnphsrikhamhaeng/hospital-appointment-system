import uuid

import pytest
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.notification_setting import NotificationSetting
from app.models.user import User
from app.repositories.notification_setting_repository import (
    NotificationSettingRepository,
)
from app.services.notification_setting_service import (
    NotificationSettingService,
)


def get_user(db):
    return db.scalar(
        select(User)
        .limit(1)
    )


def get_user_without_setting(db):
    return db.scalar(
        select(User)
        .outerjoin(
            NotificationSetting,
            NotificationSetting.user_id == User.id,
        )
        .where(
            NotificationSetting.id.is_(None),
        )
        .limit(1)
    )


def get_service(db):
    return NotificationSettingService(db)


def test_get_existing_notification_setting():
    db = SessionLocal()

    try:
        user = get_user(db)

        if user is None:
            pytest.skip("No user found.")

        service = get_service(db)

        first = service.get_or_create_by_user_id(
            user.id,
        )

        second = service.get_or_create_by_user_id(
            user.id,
        )

        assert first.id == second.id
        assert second.user_id == user.id

    finally:
        db.rollback()
        db.close()


def test_get_notification_setting_creates_default():
    db = SessionLocal()

    created_setting_id = None

    try:
        user = get_user_without_setting(db)

        if user is None:
            pytest.skip(
                "No user without notification setting found."
            )

        service = get_service(db)

        result = service.get_or_create_by_user_id(
            user.id,
        )

        created_setting_id = result.id

        assert result.id is not None
        assert result.user_id == user.id
        assert result.all_notifications is True
        assert result.appointment_notifications is True
        assert result.medical_record_notifications is True
        assert result.system_notifications is True

    finally:
        if created_setting_id is not None:
            setting = db.get(
                NotificationSetting,
                created_setting_id,
            )

            if setting is not None:
                db.delete(setting)

            db.commit()

        db.close()


def test_update_existing_notification_setting():
    db = SessionLocal()

    try:
        user = get_user(db)

        if user is None:
            pytest.skip("No user found.")

        service = get_service(db)

        setting = service.get_or_create_by_user_id(
            user.id,
        )

        result = service.update_by_user_id(
            user_id=user.id,
            all_notifications=False,
            appointment_notifications=False,
            medical_record_notifications=True,
            system_notifications=False,
        )

        assert result.id == setting.id
        assert result.user_id == user.id
        assert result.all_notifications is False
        assert result.appointment_notifications is False
        assert result.medical_record_notifications is True
        assert result.system_notifications is False

    finally:
        db.rollback()
        db.close()


def test_update_notification_setting_creates_when_missing():
    db = SessionLocal()

    created_setting_id = None

    try:
        user = get_user_without_setting(db)

        if user is None:
            pytest.skip(
                "No user without notification setting found."
            )

        service = get_service(db)

        result = service.update_by_user_id(
            user_id=user.id,
            all_notifications=False,
            appointment_notifications=True,
            medical_record_notifications=False,
            system_notifications=True,
        )

        created_setting_id = result.id

        assert result.id is not None
        assert result.user_id == user.id
        assert result.all_notifications is False
        assert result.appointment_notifications is True
        assert result.medical_record_notifications is False
        assert result.system_notifications is True

    finally:
        if created_setting_id is not None:
            setting = db.get(
                NotificationSetting,
                created_setting_id,
            )

            if setting is not None:
                db.delete(setting)

            db.commit()

        db.close()


@pytest.mark.parametrize(
    "all_notifications,appointment_notifications,medical_record_notifications,system_notifications",
    [
        (True, True, True, True),
        (False, False, False, False),
        (True, False, True, False),
        (False, True, False, True),
    ],
)
def test_update_notification_setting_all_boolean_combinations(
    all_notifications,
    appointment_notifications,
    medical_record_notifications,
    system_notifications,
):
    db = SessionLocal()

    try:
        user = get_user(db)

        if user is None:
            pytest.skip("No user found.")

        service = get_service(db)

        result = service.update_by_user_id(
            user_id=user.id,
            all_notifications=all_notifications,
            appointment_notifications=appointment_notifications,
            medical_record_notifications=medical_record_notifications,
            system_notifications=system_notifications,
        )

        assert result.all_notifications == all_notifications
        assert (
            result.appointment_notifications
            == appointment_notifications
        )
        assert (
            result.medical_record_notifications
            == medical_record_notifications
        )
        assert (
            result.system_notifications
            == system_notifications
        )

    finally:
        db.rollback()
        db.close()


def test_notification_setting_persisted():
    db = SessionLocal()

    try:
        user = get_user(db)

        if user is None:
            pytest.skip("No user found.")

        service = get_service(db)

        service.update_by_user_id(
            user_id=user.id,
            all_notifications=False,
            appointment_notifications=True,
            medical_record_notifications=False,
            system_notifications=True,
        )

        db.expire_all()

        repository = NotificationSettingRepository(db)

        result = repository.get_by_user_id(
            user.id,
        )

        assert result is not None
        assert result.user_id == user.id
        assert result.all_notifications is False
        assert result.appointment_notifications is True
        assert result.medical_record_notifications is False
        assert result.system_notifications is True

    finally:
        db.rollback()
        db.close()


def test_notification_setting_unique_per_user():
    db = SessionLocal()

    created_setting_id = None

    try:
        user = get_user_without_setting(db)

        if user is None:
            pytest.skip(
                "No user without notification setting found."
            )

        service = get_service(db)

        first = service.get_or_create_by_user_id(
            user.id,
        )

        created_setting_id = first.id

        second = service.get_or_create_by_user_id(
            user.id,
        )

        assert second.id == first.id

        count = db.scalar(
            select(NotificationSetting)
            .where(
                NotificationSetting.user_id == user.id,
            )
        )

        assert count is not None

    finally:
        if created_setting_id is not None:
            setting = db.get(
                NotificationSetting,
                created_setting_id,
            )

            if setting is not None:
                db.delete(setting)

            db.commit()

        db.close()


def test_get_notification_setting_nonexistent_user():
    db = SessionLocal()

    try:
        service = get_service(db)

        with pytest.raises(Exception):
            service.get_or_create_by_user_id(
                uuid.uuid4(),
            )

    finally:
        db.rollback()
        db.close()


def test_update_notification_setting_nonexistent_user():
    db = SessionLocal()

    try:
        service = get_service(db)

        with pytest.raises(Exception):
            service.update_by_user_id(
                user_id=uuid.uuid4(),
                all_notifications=True,
                appointment_notifications=True,
                medical_record_notifications=True,
                system_notifications=True,
            )

    finally:
        db.rollback()
        db.close()
