import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.enums import UserRoleEnum
from app.core.exceptions import ForbiddenException
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.doctor_repository import DoctorRepository


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


def get_notification_service(
    db: Session = Depends(get_db),
) -> NotificationService:
    return NotificationService(db)


def get_appointment_repository(
    db: Session = Depends(get_db),
) -> AppointmentRepository:
    return AppointmentRepository(db)

def get_doctor_repository(
    db: Session = Depends(get_db),
) -> DoctorRepository:
    return DoctorRepository(db)


@router.get(
    "",
    response_model=list[NotificationResponse],
    status_code=status.HTTP_200_OK,
)
def get_my_notifications(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(
        get_notification_service
    ),
):
    return service.get_patient_notifications(
        current_user.id,
    )


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
def get_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(
        get_notification_service
    ),
):
    notification = service.get_notification(
        notification_id,
    )

    if notification.patient_id != current_user.id:
        raise ForbiddenException()

    return notification


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
def mark_notification_as_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(
        get_notification_service
    ),
):
    notification = service.get_notification(
        notification_id,
    )

    if notification.patient_id != current_user.id:
        raise ForbiddenException()

    notification = service.mark_as_read(
    notification_id,
    )

    service.db.commit()
    service.db.refresh(notification)

    return notification


@router.post(
    "/appointments/{appointment_id}/consultation-delayed",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_consultation_delayed_notification(
    appointment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(
        get_notification_service
    ),
    appointment_repository: AppointmentRepository = Depends(
        get_appointment_repository
    ),
    doctor_repository: DoctorRepository = Depends(
        get_doctor_repository
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

    appointment = appointment_repository.get_by_id(
        appointment_id,
    )

    if appointment is None:
        raise ForbiddenException()

    if appointment.doctor_id != doctor.id:
        raise ForbiddenException()

    notification = (
        service.create_consultation_delayed_notification(
            appointment,
        )
    )

    service.db.commit()
    service.db.refresh(notification)

    return notification