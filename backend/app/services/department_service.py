import uuid

from sqlalchemy.orm import Session

from app.core.enums import DepartmentStatusEnum
from app.core.exceptions import (
    DepartmentAlreadyExistsException,
    DepartmentAlreadyInactiveException,
    DepartmentNotFoundException,
    InvalidCredentialsException,
)
from app.models.department import Department
from app.models.user import User
from app.repositories.department_repository import DepartmentRepository
from app.repositories.user_repository import UserRepository
from app.schemas.department import (
    DepartmentCreateRequest,
    DepartmentDeactivateRequest,
    DepartmentResponse,
    DepartmentUpdateRequest,
)
from app.utils.security import verify_password


class DepartmentService:
    def __init__(
        self,
        repository: DepartmentRepository,
        db: Session,
    ):
        self.repository = repository
        self.db = db
        self.user_repository = UserRepository(db)

    # ==========================================================
    # Public Methods
    # ==========================================================

    def create(
        self,
        request: DepartmentCreateRequest,
    ) -> DepartmentResponse:
        self._check_duplicate_name(request.name)

        department = self._build_department(request)

        department = self.repository.create(department)

        return DepartmentResponse.model_validate(department)

    def get(
        self,
        department_id: uuid.UUID,
    ) -> DepartmentResponse:
        department = self._get_department(department_id)

        return DepartmentResponse.model_validate(department)

    def list(
        self,
        status: DepartmentStatusEnum | None = None,
        search: str | None = None,
    ) -> list[DepartmentResponse]:
        # Default behavior: show ACTIVE departments only.
        # When searching, allow searching both ACTIVE and INACTIVE.
        if status is None and not search:
            status = DepartmentStatusEnum.ACTIVE

        departments = self.repository.get_departments(
            status=status,
            search=search,
        )

        return [
            DepartmentResponse.model_validate(department)
            for department in departments
        ]

    def update(
        self,
        department_id: uuid.UUID,
        request: DepartmentUpdateRequest,
    ) -> DepartmentResponse:
        department = self._get_department(department_id)

        if (
            request.name is not None
            and request.name != department.name
        ):
            self._check_duplicate_name(
                request.name,
                exclude_department_id=department.id,
            )

        update_data = request.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(department, field, value)

        department = self.repository.update(department)

        return DepartmentResponse.model_validate(department)

    def delete(
        self,
        department_id: uuid.UUID,
        request: DepartmentDeactivateRequest,
        current_user: User,
    ) -> DepartmentResponse:
        department = self._get_department(department_id)

        if department.status == DepartmentStatusEnum.INACTIVE:
            raise DepartmentAlreadyInactiveException()

        staff = self.user_repository.get_by_id(
            current_user.id,
        )

        if staff is None:
            raise InvalidCredentialsException()

        if not verify_password(
            request.password,
            staff.password,
        ):
            raise InvalidCredentialsException()

        department.status = DepartmentStatusEnum.INACTIVE

        department = self.repository.update(department)

        return DepartmentResponse.model_validate(department)

    # ==========================================================
    # Private Methods
    # ==========================================================

    def _get_department(
        self,
        department_id: uuid.UUID,
    ) -> Department:
        department = self.repository.get_by_id(department_id)

        if department is None:
            raise DepartmentNotFoundException()

        return department

    def _check_duplicate_name(
        self,
        name: str,
        exclude_department_id: uuid.UUID | None = None,
    ) -> None:
        department = self.repository.get_by_name(name)

        if department is None:
            return

        if (
            exclude_department_id is not None
            and department.id == exclude_department_id
        ):
            return

        raise DepartmentAlreadyExistsException()

    def _build_department(
        self,
        request: DepartmentCreateRequest,
    ) -> Department:
        return Department(
            name=request.name,
            description=request.description,
            image_url=request.image_url,
            slot_duration_minutes=request.slot_duration_minutes,
            status=DepartmentStatusEnum.ACTIVE,
        )