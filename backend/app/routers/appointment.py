import uuid

from datetime import date

from fastapi import APIRouter, Depends, Query, status

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.core.dependencies import get_current_user

from app.core.enums import (
    AppointmentStatusEnum,
    UserRoleEnum,
)

from app.core.exceptions import ForbiddenException

from app.models.user import User

from app.schemas.appointment import (
    AppointmentCancelRequest,
    AppointmentCreateRequest,
    AppointmentRescheduleRequest,
    AppointmentResponse,
    AppointmentStatusUpdateRequest,
    DoctorScheduleResponse,
)
from app.schemas.user import UserResponse

from app.services.appointment_service import AppointmentService
from app.repositories.doctor_repository import DoctorRepository


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)


def get_appointment_service(
    db: Session = Depends(get_db),
) -> AppointmentService:

    return AppointmentService(db)


def get_doctor_repository(
    db: Session = Depends(get_db),
) -> DoctorRepository:
    return DoctorRepository(db)


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    patient_id: uuid.UUID,
    request: AppointmentCreateRequest,
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):

    return service.create_appointment(
        patient_id,
        request,
    )


@router.get(
    "/search",
    response_model=list[AppointmentResponse],
)
def search_appointments(
    patient_id: uuid.UUID | None = Query(default=None),
    doctor_id: uuid.UUID | None = Query(default=None),
    appointment_date: date | None = Query(default=None),
    status: AppointmentStatusEnum | None = Query(default=None),
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):

    return service.search_appointments(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        status=status,
    )


@router.get(
    "/my",
    response_model=list[AppointmentResponse],
)
def get_my_appointments(
    current_user: User = Depends(get_current_user),
    doctor_repository: DoctorRepository = Depends(
        get_doctor_repository
    ),
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):

    if current_user.role != UserRoleEnum.DOCTOR:
        raise ForbiddenException()

    doctor = doctor_repository.get_by_user_id(
        current_user.id
    )

    if doctor is None:
        raise ForbiddenException(
            detail="Current user is not a doctor."
        )

    return service.get_doctor_appointments(
        doctor.id
    )


@router.get(
    "/my/schedule",
    response_model=list[DoctorScheduleResponse],
)
def get_my_schedule(
    appointment_date: date,
    current_user: User = Depends(get_current_user),
    doctor_repository: DoctorRepository = Depends(
        get_doctor_repository
    ),
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):

    if current_user.role != UserRoleEnum.DOCTOR:
        raise ForbiddenException()

    doctor = doctor_repository.get_by_user_id(
        current_user.id
    )

    if doctor is None:
        raise ForbiddenException(
            detail="Current user is not a doctor."
        )

    return service.get_doctor_schedule(
        doctor.id,
        appointment_date,
    )


@router.get(
    "/{appointment_id}/patient",
    response_model=UserResponse,
)
def get_appointment_patient(
    appointment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):

    return service.get_appointment_patient(
        appointment_id,
        current_user,
    )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
def get_appointment(
    appointment_id: uuid.UUID,
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):

    return service.get_appointment(
        appointment_id
    )


@router.get(
    "/patients/{patient_id}",
    response_model=list[AppointmentResponse],
)
def get_patient_appointments(
    patient_id: uuid.UUID,
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):

    return service.get_patient_appointments(
        patient_id
    )


@router.get(
    "/doctors/{doctor_id}",
    response_model=list[AppointmentResponse],
)
def get_doctor_appointments(
    doctor_id: uuid.UUID,
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):

    return service.get_doctor_appointments(
        doctor_id
    )


@router.get(
    "/doctors/{doctor_id}/schedule",
    response_model=list[DoctorScheduleResponse],
)
def get_doctor_schedule(
    doctor_id: uuid.UUID,
    appointment_date: date,
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):

    return service.get_doctor_schedule(
        doctor_id,
        appointment_date,
    )


@router.patch(
    "/{appointment_id}/reschedule",
    response_model=AppointmentResponse,
)
def reschedule_appointment(
    appointment_id: uuid.UUID,
    request: AppointmentRescheduleRequest,
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):

    return service.reschedule_appointment(
        appointment_id,
        request,
    )


@router.patch(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
)
def cancel_appointment(
    appointment_id: uuid.UUID,
    request: AppointmentCancelRequest,
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):

    return service.cancel_appointment(
        appointment_id,
        request,
    )


@router.patch(
    "/{appointment_id}/status",
    response_model=AppointmentResponse,
)
def update_status(
    appointment_id: uuid.UUID,
    request: AppointmentStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):

    if current_user.role not in {
        UserRoleEnum.DOCTOR,
        UserRoleEnum.HOSPITAL_STAFF,
    }:
        raise ForbiddenException()

    return service.update_status(
        appointment_id,
        request,
        current_user,
    )