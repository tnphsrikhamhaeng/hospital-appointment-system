from __future__ import annotations
import uuid

from sqlalchemy.orm import Session

from app.core.enums import (
    UserRoleEnum,
    UserStatusEnum,
)
from app.core.exceptions import (
    EmailAlreadyExistsException,
    PhoneNumberAlreadyExistsException,
    UsernameAlreadyExistsException,
     InvalidCredentialsException,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.staff import (
    StaffCreateRequest,
    StaffDeactivateRequest,
    StaffUpdateRequest,
)
from app.schemas.user import UserResponse
from app.utils.security import hash_password, verify_password

class StaffService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        
    def list_staff(
        self,
        status: UserStatusEnum | None = None,
        search: str | None = None,
    ) -> list[UserResponse]:
        staff_list = self.user_repository.list_staff(
            status=status,
            search=search,
        )

        return [
            UserResponse.model_validate(staff)
            for staff in staff_list
        ]

    def create_staff(
        self,
        request: StaffCreateRequest,
    ) -> UserResponse:

        try:
            if self.user_repository.get_by_username(
                request.username
            ):
                raise UsernameAlreadyExistsException()

            if self.user_repository.get_by_email_and_role(
                request.email,
                UserRoleEnum.HOSPITAL_STAFF,
            ):
                raise EmailAlreadyExistsException()

            if self.user_repository.get_by_phone_number_and_role(
                request.phone_number,
                UserRoleEnum.HOSPITAL_STAFF,
            ):
                raise PhoneNumberAlreadyExistsException()

            user = User(
                username=request.username,
                first_name=request.first_name,
                last_name=request.last_name,
                phone_number=request.phone_number,
                email=request.email,
                password=hash_password(request.password),
                role=UserRoleEnum.HOSPITAL_STAFF,
                status=UserStatusEnum.ACTIVE,
                gender=None,
                date_of_birth=None,
            )

            user = self.user_repository.create(user)

            self.db.commit()
            self.db.refresh(user)

            return UserResponse.model_validate(user)

        except Exception:
            self.db.rollback()
            raise
    
    def update_staff(
        self,
        staff_id: uuid.UUID,
        request: StaffUpdateRequest,
    ) -> UserResponse:
        try:
            staff = self.user_repository.get_by_id(staff_id)

            if staff is None or staff.role != UserRoleEnum.HOSPITAL_STAFF:
                raise ValueError("Staff not found")

            existing_username = self.user_repository.get_by_username(
                request.username,
            )
            if (
                existing_username
                and existing_username.id != staff.id
            ):
                raise UsernameAlreadyExistsException()

            existing_email = self.user_repository.get_by_email_and_role(
                request.email,
                UserRoleEnum.HOSPITAL_STAFF,
            )
            if (
                existing_email
                and existing_email.id != staff.id
            ):
                raise EmailAlreadyExistsException()

            existing_phone = (
                self.user_repository.get_by_phone_number_and_role(
                    request.phone_number,
                    UserRoleEnum.HOSPITAL_STAFF,
                )
            )
            if (
                existing_phone
                and existing_phone.id != staff.id
            ):
                raise PhoneNumberAlreadyExistsException()

            staff.username = request.username
            staff.first_name = request.first_name
            staff.last_name = request.last_name
            staff.phone_number = request.phone_number
            staff.email = request.email

            staff = self.user_repository.update(staff)

            self.db.commit()
            self.db.refresh(staff)

            return UserResponse.model_validate(staff)

        except Exception:
            self.db.rollback()
            raise
    
    def deactivate_staff(
        self,
        staff_id: uuid.UUID,
        request: StaffDeactivateRequest,
        current_user: User,
    ) -> UserResponse:
        try:
            staff = self.user_repository.get_by_id(staff_id)

            if staff is None or staff.role != UserRoleEnum.HOSPITAL_STAFF:
                raise ValueError("Staff not found")

            if staff.status == UserStatusEnum.INACTIVE:
                raise ValueError("Staff is already inactive")

            current_staff = self.user_repository.get_by_id(
                current_user.id,
            )

            if current_staff is None:
                raise InvalidCredentialsException()

            if not verify_password(
                request.password,
                current_staff.password,
            ):
                raise InvalidCredentialsException()

            staff.status = UserStatusEnum.INACTIVE

            staff = self.user_repository.update(staff)

            self.db.commit()
            self.db.refresh(staff)

            return UserResponse.model_validate(staff)

        except Exception:
            self.db.rollback()
            raise