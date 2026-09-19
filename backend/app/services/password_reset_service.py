from datetime import datetime, timedelta, timezone
import secrets

from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken
from app.repositories.password_reset_token import PasswordResetTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.password_reset import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    StaffForgotPasswordRequest,
)
from app.utils.security import hash_password
from app.core.enums import UserRoleEnum
from app.core.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UserNotFoundException,
)


class PasswordResetService:
    RESET_TOKEN_EXPIRE_MINUTES = 15

    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.reset_token_repository = PasswordResetTokenRepository(db)

    def request_reset(
        self,
        request: ForgotPasswordRequest,
    ) -> str:
        user = self.user_repository.get_by_email(
            request.email,
        )

        if user is None:
            raise UserNotFoundException()

        token = secrets.token_urlsafe(32)

        expires_at = datetime.now(
            timezone.utc,
        ) + timedelta(
            minutes=self.RESET_TOKEN_EXPIRE_MINUTES,
        )

        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )

        self.reset_token_repository.create(
            reset_token,
        )

        self.db.commit()

        return token

    def reset_password(
        self,
        request: ResetPasswordRequest,
    ) -> None:
        reset_token = self.reset_token_repository.get_by_token(
            request.reset_token,
        )

        if reset_token is None:
            raise NotFoundException("Invalid reset token")

        now = datetime.now(timezone.utc)

        if reset_token.used_at is not None:
            raise ConflictException("Reset token already used")

        if reset_token.expires_at <= now:
            raise ConflictException("Reset token expired")

        user = self.user_repository.get_by_id(
            reset_token.user_id,
        )

        if user is None:
            raise UserNotFoundException()

        user.password = hash_password(
            request.new_password,
        )

        self.reset_token_repository.mark_as_used(
            reset_token,
        )

        self.user_repository.update(
            user,
        )

        self.db.commit()

    def request_staff_reset(
        self,
        request: StaffForgotPasswordRequest,
    ) -> str:
        user = self.user_repository.get_by_username(
            request.username,
        )

        if user is None:
            raise UserNotFoundException()

        if user.role not in (
            UserRoleEnum.DOCTOR,
            UserRoleEnum.HOSPITAL_STAFF,
        ):
            raise ForbiddenException()

        token = secrets.token_urlsafe(32)

        expires_at = datetime.now(
            timezone.utc,
        ) + timedelta(
            minutes=self.RESET_TOKEN_EXPIRE_MINUTES,
        )

        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )

        self.reset_token_repository.create(
            reset_token,
        )

        self.db.commit()

        return token