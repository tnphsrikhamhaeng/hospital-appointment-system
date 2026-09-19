from sqlalchemy.orm import Session

from app.core.exceptions import InvalidCredentialsException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.change_password import ChangePasswordRequest
from app.utils.security import hash_password, verify_password


class ChangePasswordService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def change_password(
        self,
        current_user: User,
        request: ChangePasswordRequest,
    ) -> None:
        user = self.user_repository.get_by_id(
            current_user.id,
        )

        if user is None:
            raise InvalidCredentialsException()

        if not verify_password(
            plain_password=request.current_password,
            hashed_password=user.password,
        ):
            raise InvalidCredentialsException()

        user.password = hash_password(
            request.new_password,
        )

        self.user_repository.update(user)

        self.db.commit()