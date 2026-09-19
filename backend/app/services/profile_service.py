from sqlalchemy.orm import Session

from app.core.exceptions import (
    EmailAlreadyExistsException,
    PhoneNumberAlreadyExistsException,
    UserNotFoundException,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    ProfileResponse,
    UpdateProfileRequest,
)


class ProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def get_profile(
        self,
        current_user: User,
    ) -> ProfileResponse:
        user = self.user_repository.get_by_id(
            current_user.id,
        )

        if user is None:
            raise UserNotFoundException()

        return ProfileResponse.model_validate(user)

    def update_profile(
        self,
        current_user: User,
        request: UpdateProfileRequest,
    ) -> ProfileResponse:
        user = self.user_repository.get_by_id(
            current_user.id,
        )

        if user is None:
            raise UserNotFoundException()

        if request.email is not None:
            existing_user = self.user_repository.get_by_email(
                request.email,
            )

            if (
                existing_user is not None
                and existing_user.id != user.id
            ):
                raise EmailAlreadyExistsException()

        if request.phone_number is not None:
            existing_user = self.user_repository.get_by_phone_number(
                request.phone_number,
            )

            if (
                existing_user is not None
                and existing_user.id != user.id
            ):
                raise PhoneNumberAlreadyExistsException()

        if request.first_name is not None:
            user.first_name = request.first_name

        if request.last_name is not None:
            user.last_name = request.last_name

        if request.phone_number is not None:
            user.phone_number = request.phone_number

        if request.email is not None:
            user.email = request.email

        self.user_repository.update(user)

        self.db.commit()
        self.db.refresh(user)

        return ProfileResponse.model_validate(user)