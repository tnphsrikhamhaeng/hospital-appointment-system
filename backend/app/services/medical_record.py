from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.core.enums import AppointmentStatusEnum
from app.core.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    MedicalRecordAppointmentNotCheckedInException,
)
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.medical_record_repository import (
    MedicalRecordRepository,
)
from app.schemas.medical_record_schema import (
    DoctorMedicalHistoryResponse,
    MedicalRecordCreate,
    MedicalRecordResponse,
    MedicalRecordUpdate,
)

class MedicalRecordService:

    def __init__(self, db: Session):
        self.db = db

        self.medical_record_repository = (
            MedicalRecordRepository(db)
        )
        self.appointment_repository = (
            AppointmentRepository(db)
        )

    def create_medical_record(
        self,
        doctor_id: uuid.UUID,
        request: MedicalRecordCreate,
    ) -> MedicalRecordResponse:

        appointment = self._get_appointment_or_404(
            request.appointment_id
        )

        self._ensure_appointment_checked_in(
            appointment
        )

        self._ensure_doctor_owns_appointment(
            doctor_id=doctor_id,
            appointment_doctor_id=appointment.doctor_id,
        )

        self._ensure_medical_record_not_exists(
            appointment.id
        )

        medical_record = MedicalRecord(
            appointment_id=appointment.id,
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            chief_complaint=request.chief_complaint,
            present_illness=request.present_illness,
            physical_examination=request.physical_examination,
            diagnosis=request.diagnosis,
            treatment=request.treatment,
            recommendation=request.recommendation,
            note=request.note,
        )

        medical_record = (
            self.medical_record_repository.create(
                medical_record
            )
        )

        appointment.status = (
            AppointmentStatusEnum.COMPLETED
        )

        self.appointment_repository.update(
            appointment
        )

        self.db.commit()

        self.db.refresh(medical_record)

        return MedicalRecordResponse.model_validate(
            medical_record
        )

    def get_medical_record(
        self,
        medical_record_id: uuid.UUID,
        *,
        patient_id: uuid.UUID | None = None,
        doctor_id: uuid.UUID | None = None,
    ) -> MedicalRecordResponse:

        medical_record = (
            self.medical_record_repository.get_by_id(
                medical_record_id
            )
        )

        if medical_record is None:
            raise NotFoundException(
                detail="Medical record not found."
            )

        # Patient สามารถดูได้เฉพาะ Medical Record ของตัวเอง
        if patient_id is not None:
            if medical_record.patient_id != patient_id:
                raise ForbiddenException()

        # Doctor สามารถดูได้เฉพาะ Medical Record
        # ที่ตนเองเป็นผู้บันทึก
        if doctor_id is not None:
            if medical_record.doctor_id != doctor_id:
                raise ForbiddenException()

        return MedicalRecordResponse.model_validate(
            medical_record
        )

    def get_patient_medical_records(
        self,
        patient_id: uuid.UUID,
    ) -> list[MedicalRecordResponse]:

        medical_records = (
            self.medical_record_repository.get_by_patient(
                patient_id
            )
        )

        return [
            MedicalRecordResponse.model_validate(
                medical_record
            )
            for medical_record in medical_records
        ]

    def get_doctor_medical_history(
        self,
        doctor_id: uuid.UUID,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[DoctorMedicalHistoryResponse]:

        appointments = self.appointment_repository.search(
            doctor_id=doctor_id,
            date_from=date_from,
            date_to=date_to,
        )

        history = []

        for appointment in appointments:
            if appointment.status not in (
                AppointmentStatusEnum.COMPLETED,
                AppointmentStatusEnum.NO_SHOW,
            ):
                continue

            medical_record = (
                self.medical_record_repository
                .get_by_appointment_id(
                    appointment.id
                )
            )

            history.append(
            DoctorMedicalHistoryResponse(
                appointment_id=appointment.id,
                appointment_date=appointment.appointment_date,
                start_time=appointment.start_time,
                end_time=appointment.end_time,
                patient_id=appointment.patient_id,
                patient_name=(
                    f"{appointment.patient.first_name} "
                    f"{appointment.patient.last_name}"
                ),
                status=appointment.status,
                medical_record=(
                        MedicalRecordResponse.model_validate(
                            medical_record
                        )
                        if medical_record is not None
                        else None
                    ),
                )
            )

        return history

    def update_medical_record(
        self,
        medical_record_id: uuid.UUID,
        doctor_id: uuid.UUID,
        request: MedicalRecordUpdate,
    ) -> MedicalRecordResponse:

        medical_record = (
            self.medical_record_repository.get_by_id(
                medical_record_id
            )
        )

        if medical_record is None:
            raise NotFoundException(
                detail="Medical record not found."
            )

        if medical_record.doctor_id != doctor_id:
            raise ForbiddenException()

        update_data = request.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(
                medical_record,
                field,
                value,
            )

        medical_record = (
            self.medical_record_repository.update(
                medical_record
            )
        )

        self.db.commit()
        self.db.refresh(medical_record)

        return MedicalRecordResponse.model_validate(
            medical_record
        )

    def _get_appointment_or_404(
        self,
        appointment_id: uuid.UUID,
    ) -> Appointment:

        appointment = (
            self.appointment_repository.get_by_id(
                appointment_id
            )
        )

        if appointment is None:
            raise NotFoundException(
                detail="Appointment not found."
            )

        return appointment

    def _ensure_appointment_checked_in(
        self,
        appointment: Appointment,
    ) -> None:

        if appointment.status not in (
            AppointmentStatusEnum.CHECKED_IN,
            AppointmentStatusEnum.IN_PROGRESS,
        ):
            raise MedicalRecordAppointmentNotCheckedInException()

    def _ensure_doctor_owns_appointment(
        self,
        *,
        doctor_id: uuid.UUID,
        appointment_doctor_id: uuid.UUID,
    ) -> None:

        if doctor_id != appointment_doctor_id:
            raise ConflictException(
                detail=(
                    "Doctor is not assigned to this appointment."
                )
            )

    def _ensure_medical_record_not_exists(
        self,
        appointment_id: uuid.UUID,
    ) -> None:

        medical_record = (
            self.medical_record_repository
            .get_by_appointment_id(
                appointment_id
            )
        )

        if medical_record is not None:
            raise ConflictException(
                detail=(
                    "Medical record already exists "
                    "for this appointment."
                )
            )