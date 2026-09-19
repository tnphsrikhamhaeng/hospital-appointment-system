import uuid

from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.core.dependencies import get_current_user

from app.schemas.appointment_qr import (
    AppointmentQRCodeCheckInRequest,
    AppointmentQRCodeCheckInResponse,
    AppointmentQRCodeResponse,
    AppointmentQRCodeStaffCheckInPreviewResponse,
)

from app.services.appointment_qr import (
    AppointmentQRCodeService,
)

from app.models.user import User


router = APIRouter(
    prefix="/appointment-qr",
    tags=["Appointment QR"],
)


def get_appointment_qr_service(
    db: Session = Depends(get_db),
) -> AppointmentQRCodeService:

    return AppointmentQRCodeService(db)


@router.get(
    "/{appointment_id}",
    response_model=AppointmentQRCodeResponse,
)
def get_qr(
    appointment_id: uuid.UUID,
    service: AppointmentQRCodeService = Depends(
        get_appointment_qr_service
    ),
):

    return service.get_qr(
        appointment_id
    )


@router.post(
    "/check-in",
    response_model=AppointmentQRCodeCheckInResponse,
    status_code=status.HTTP_200_OK,
)
def check_in(
    request: AppointmentQRCodeCheckInRequest,
    current_user: User = Depends(get_current_user),
    service: AppointmentQRCodeService = Depends(
        get_appointment_qr_service
    ),
):

    return service.check_in(
        request,
        current_user,
    )


@router.post(
    "/staff-check-in-preview",
    response_model=AppointmentQRCodeStaffCheckInPreviewResponse,
    status_code=status.HTTP_200_OK,
)
def staff_check_in_preview(
    request: AppointmentQRCodeCheckInRequest,
    current_user: User = Depends(get_current_user),
    service: AppointmentQRCodeService = Depends(
        get_appointment_qr_service
    ),
):

    return service.staff_check_in_preview(
        request,
        current_user,
    )


@router.post(
    "/staff-check-in",
    response_model=AppointmentQRCodeCheckInResponse,
    status_code=status.HTTP_200_OK,
)
def staff_check_in(
    request: AppointmentQRCodeCheckInRequest,
    current_user: User = Depends(get_current_user),
    service: AppointmentQRCodeService = Depends(
        get_appointment_qr_service
    ),
):

    return service.staff_check_in(
        request,
        current_user,
    )