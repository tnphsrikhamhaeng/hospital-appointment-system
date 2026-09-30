import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal
from app.services.notification_scheduler import (
    run_reminder_3_days,
    run_reminder_1_day,
    run_reminder_30_minutes,
)


logger = logging.getLogger(__name__)


scheduler = BackgroundScheduler(
    timezone="Asia/Bangkok",
)


def _run_reminder_3_days():
    logger.info("Running 3-day reminder scheduler")

    db = SessionLocal()

    try:
        run_reminder_3_days(db)
    except Exception:
        db.rollback()
        logger.exception(
            "3-day reminder scheduler failed"
        )
    finally:
        db.close()


def _run_reminder_1_day():
    logger.info("Running 1-day reminder scheduler")

    db = SessionLocal()

    try:
        run_reminder_1_day(db)
    except Exception:
        db.rollback()
        logger.exception(
            "1-day reminder scheduler failed"
        )
    finally:
        db.close()


def _run_reminder_30_minutes():
    print(">>> Running 30-minute reminder scheduler")

    db = SessionLocal()

    try:
        run_reminder_30_minutes(db)
    except Exception:
        db.rollback()
        logger.exception(
            "30-minute reminder scheduler failed"
        )
    finally:
        db.close()


def start_scheduler():
    if scheduler.running:
        return

    scheduler.add_job(
        _run_reminder_3_days,
        trigger="interval",
        hours=1,
        id="reminder_3_days",
        replace_existing=True,
    )

    scheduler.add_job(
        _run_reminder_1_day,
        trigger="interval",
        hours=1,
        id="reminder_1_day",
        replace_existing=True,
    )

    scheduler.add_job(
        _run_reminder_30_minutes,
        trigger="interval",
        minutes=1,
        id="reminder_30_minutes",
        replace_existing=True,
    )

    scheduler.start()

    print(">>> Notification scheduler started")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)

        logger.info(
            "Notification scheduler stopped"
        )