from datetime import date, time

from app.core.database import SessionLocal
from app.core.enums import AppointmentStatusEnum
from app.models.appointment import Appointment


APPOINTMENT_ID = "711b2c7e-52a9-47fa-ac84-55a83ff96eef"

TEST_DATE = date(2026, 9, 4)
TEST_START_TIME = time(18, 30)
TEST_END_TIME = time(19, 0)


def main():
    db = SessionLocal()

    appointment = None
    original_values = {}

    try:
        appointment = db.get(
            Appointment,
            APPOINTMENT_ID,
        )

        if appointment is None:
            raise RuntimeError("Appointment not found.")

        original_values = {
            "appointment_date": appointment.appointment_date,
            "start_time": appointment.start_time,
            "end_time": appointment.end_time,
            "status": appointment.status,
            "confirmed_at": appointment.confirmed_at,
        }

        print("Original appointment:")
        print(f"  date   : {appointment.appointment_date}")
        print(f"  start  : {appointment.start_time}")
        print(f"  end    : {appointment.end_time}")
        print(f"  status : {appointment.status}")

        appointment.appointment_date = TEST_DATE
        appointment.start_time = TEST_START_TIME
        appointment.end_time = TEST_END_TIME
        appointment.status = AppointmentStatusEnum.CONFIRMED

        db.commit()

        print()
        print("Test appointment prepared:")
        print(f"  date   : {appointment.appointment_date}")
        print(f"  start  : {appointment.start_time}")
        print(f"  end    : {appointment.end_time}")
        print(f"  status : {appointment.status}")

        print()
        print("You can now test:")
        print("GET  /appointment-qr/{appointment_id}")
        print("POST /appointment-qr/check-in")
        print()
        print(
            "IMPORTANT: Do not close this process "
            "until the check-in test is finished."
        )
        print(
            "Press Enter to restore the original appointment."
        )

        input()

    finally:
        if appointment is not None and original_values:
            appointment.appointment_date = (
                original_values["appointment_date"]
            )
            appointment.start_time = (
                original_values["start_time"]
            )
            appointment.end_time = (
                original_values["end_time"]
            )
            appointment.status = original_values["status"]
            appointment.confirmed_at = (
                original_values["confirmed_at"]
            )

            db.commit()

            print()
            print("Original appointment restored.")
            print(f"  date   : {appointment.appointment_date}")
            print(f"  start  : {appointment.start_time}")
            print(f"  end    : {appointment.end_time}")
            print(f"  status : {appointment.status}")

        db.close()


if __name__ == "__main__":
    main()