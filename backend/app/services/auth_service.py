from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse
from app.utils.security import hash_password, create_access_token, verify_password
from app.core.enums import UserRoleEnum, UserStatusEnum
from app.core.exceptions import (
    UsernameAlreadyExistsException,
    EmailAlreadyExistsException,
    PhoneNumberAlreadyExistsException,
    InvalidCredentialsException,
    ForbiddenException,
    InactiveAccountException,
)

class AuthService:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db
        self.user_repository = UserRepository(db)


    def _check_username_exists(
        self,
        username: str,
    ) -> None:
        user = self.user_repository.get_by_username(username)

        if user is not None:
            raise UsernameAlreadyExistsException()


    def _check_email_exists(
        self,
        email: str,
    ) -> None:
        user = self.user_repository.get_by_email(email)

        if user is not None:
            raise EmailAlreadyExistsException()


    def _check_phone_number_exists(
        self,
        phone_number: str,
    ) -> None:
        user = self.user_repository.get_by_phone_number(phone_number)

        if user is not None:
            raise PhoneNumberAlreadyExistsException()


    def _build_patient(
          self,
          request: RegisterRequest,
      ) -> User:
          return User(
              username=request.username,
              first_name=request.first_name,
              last_name=request.last_name,
              date_of_birth=request.date_of_birth,
              gender=request.gender,
              phone_number=request.phone_number,
              email=request.email,
              password=hash_password(request.password),
              role=UserRoleEnum.PATIENT,
              status=UserStatusEnum.ACTIVE,
          )
          
          
    def _get_user_by_username(
        self,
        username: str,
    ) -> User:
        user = self.user_repository.get_by_username(
            username=username,
        )
        if user is None:
            raise InvalidCredentialsException()

        return user
      
      
    def _verify_password(
        self,
        plain_password: str,
        hashed_password: str,
    ) -> None:
        if not verify_password(
            plain_password=plain_password,
            hashed_password=hashed_password,
        ):
            raise InvalidCredentialsException()
          
    def _validate_login_user(
        self,
        user: User,
    ) -> None:
        if user.role != UserRoleEnum.PATIENT:
            raise ForbiddenException()

        if user.status != UserStatusEnum.ACTIVE:
            raise InactiveAccountException()
          
          
    def register(
          self,
          request: RegisterRequest,
      ) -> RegisterResponse:
          try:
              self._check_username_exists(request.username)
              self._check_email_exists(request.email)
              self._check_phone_number_exists(request.phone_number)

              patient = self._build_patient(request)

              self.user_repository.create(patient)

              self.db.commit()
              self.db.refresh(patient)

              return RegisterResponse(
                  id=patient.id,
                  username=patient.username,
                  email=patient.email,
                  message="Register successfully.",
              )

          except Exception:
              self.db.rollback()
              raise
            
            
    def login(
        self,
        request: LoginRequest,
    ) -> LoginResponse:
        try:
            user = self._get_user_by_username(
                username=request.username,
            )

            self._verify_password(
                plain_password=request.password,
                hashed_password=user.password,
            )

            self._validate_login_user(
                user=user,
            )

            access_token = create_access_token(
                data={
                    "sub": str(user.id),
                },
            )

            return LoginResponse(
                access_token=access_token,
            )

        except Exception:
            self.db.rollback()
            raise