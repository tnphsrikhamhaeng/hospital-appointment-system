import uuid

from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.enums import UserRoleEnum
from app.core.exceptions import (
    ForbiddenException,
    ForbiddenExceptiondoctor,
)
from app.models.user import User
from app.schemas.medical_record_schema import (
    DoctorMedicalHistoryResponse,
    MedicalRecordCreate,
    MedicalRecordResponse,
    MedicalRecordUpdate,
)
from app.services.medical_record import MedicalRecordService
from app.repositories.doctor_repository import DoctorRepository


router = APIRouter(
    prefix="/medical-records",
    tags=["Medical Records"],
)


def get_medical_record_service(
    db: Session = Depends(get_db),
) -> MedicalRecordService:
    return MedicalRecordService(db)


@router.post(
    "",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_medical_record(
    request: MedicalRecordCreate,
    service: MedicalRecordService = Depends(
        get_medical_record_service
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doctor_repository = DoctorRepository(db)

    doctor = doctor_repository.get_by_user_id(
        current_user.id
    )

    if doctor is None:
        raise ForbiddenException(
            detail="Current user is not a doctor."
        )

    return service.create_medical_record(
        doctor.id,
        request,
    )


@router.get(
    "",
    response_model=list[MedicalRecordResponse],
)
def get_my_medical_records(
    service: MedicalRecordService = Depends(
        get_medical_record_service
    ),
    current_user: User = Depends(get_current_user),
):
    return service.get_patient_medical_records(
        current_user.id
    )


@router.get(
    "/doctor/history",
    response_model=list[DoctorMedicalHistoryResponse],
)
def get_doctor_medical_history(
    date_from: date | None = None,
    date_to: date | None = None,
    service: MedicalRecordService = Depends(
        get_medical_record_service
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doctor_repository = DoctorRepository(db)

    doctor = doctor_repository.get_by_user_id(
        current_user.id
    )

    if doctor is None:
        raise ForbiddenException(
            detail="Current user is not a doctor."
        )

    return service.get_doctor_medical_history(
        doctor_id=doctor.id,
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/{medical_record_id}",
    response_model=MedicalRecordResponse,
)
def get_medical_record(
    medical_record_id: uuid.UUID,
    service: MedicalRecordService = Depends(
        get_medical_record_service
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Doctor
    if current_user.role == UserRoleEnum.DOCTOR:
        doctor_repository = DoctorRepository(db)

        doctor = doctor_repository.get_by_user_id(
            current_user.id
        )

        if doctor is None:
            raise ForbiddenException(
                detail="Current user is not a doctor."
            )

        return service.get_medical_record(
            medical_record_id,
            doctor_id=doctor.id,
        )

    # Patient
    if current_user.role == UserRoleEnum.PATIENT:
        return service.get_medical_record(
            medical_record_id,
            patient_id=current_user.id,
        )

    # Staff และ Role อื่น ๆ ไม่มีสิทธิ์ดู Medical Record รายการนี้
    raise ForbiddenException()


@router.patch(
    "/{medical_record_id}",
    response_model=MedicalRecordResponse,
)
def update_medical_record(
    medical_record_id: uuid.UUID,
    request: MedicalRecordUpdate,
    service: MedicalRecordService = Depends(
        get_medical_record_service
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doctor_repository = DoctorRepository(db)

    doctor = doctor_repository.get_by_user_id(
        current_user.id
    )

    if doctor is None:
        raise ForbiddenExceptiondoctor()

    return service.update_medical_record(
        medical_record_id,
        doctor.id,
        request,
    )