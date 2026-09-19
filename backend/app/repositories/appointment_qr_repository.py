from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.appointment_qr_code import AppointmentQRCode


class AppointmentQRCodeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_appointment(
        self,
        appointment_id: UUID,
    ) -> AppointmentQRCode | None:
        statement = (
            select(AppointmentQRCode)
            .where(AppointmentQRCode.appointment_id == appointment_id)
        )

        return self.db.scalar(statement)

    def get_by_token(
        self,
        token: str,
    ) -> AppointmentQRCode | None:
        statement = (
            select(AppointmentQRCode)
            .where(AppointmentQRCode.token == token)
        )

        return self.db.scalar(statement)

    def create(
        self,
        qr_code: AppointmentQRCode,
    ) -> AppointmentQRCode:
        self.db.add(qr_code)
        self.db.flush()
        self.db.refresh(qr_code)

        return qr_code

    def update(
        self,
        qr_code: AppointmentQRCode,
    ) -> AppointmentQRCode:
        self.db.flush()
        self.db.refresh(qr_code)

        return qr_code