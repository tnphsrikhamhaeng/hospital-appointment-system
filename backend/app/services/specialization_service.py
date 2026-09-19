import uuid

from app.core.enums import SpecializationStatusEnum
from app.core.exceptions import (
    DepartmentNotFoundException,
    SpecializationAlreadyExistsException,
    SpecializationAlreadyInactiveException,
    SpecializationNotFoundException,
)
from app.models.specialization import Specialization
from app.repositories.department_repository import DepartmentRepository
from app.repositories.specialization_repository import SpecializationRepository
from app.schemas.specialization import (
    SpecializationCreateRequest,
    SpecializationResponse,
    SpecializationUpdateRequest,
)


class SpecializationService:
    def __init__(
        self,
        specialization_repository: SpecializationRepository,
        department_repository: DepartmentRepository,
    ):
        self.specialization_repository = specialization_repository
        self.department_repository = department_repository

    # ==========================================================
    # Public Methods
    # ==========================================================

    def create(
        self,
        request: SpecializationCreateRequest,
    ) -> SpecializationResponse:
        self._validate_department(request.department_id)

        self._check_duplicate_name(
            department_id=request.department_id,
            name=request.name,
        )

        specialization = self._build_specialization(request)

        specialization = self.specialization_repository.create(
            specialization
        )

        return SpecializationResponse.model_validate(specialization)

    def get(
        self,
        specialization_id: uuid.UUID,
    ) -> SpecializationResponse:
        specialization = self._get_specialization(specialization_id)

        return SpecializationResponse.model_validate(specialization)

    def list(
        self,
        status: SpecializationStatusEnum | None = None,
        search: str | None = None,
    ) -> list[SpecializationResponse]:
        # Default behavior: show ACTIVE specializations only.
        # When searching, allow searching both ACTIVE and INACTIVE.
        if status is None and not search:
            status = SpecializationStatusEnum.ACTIVE

        specializations = self.specialization_repository.get_specializations(
            status=status,
            search=search,
        )

        return [
            SpecializationResponse.model_validate(specialization)
            for specialization in specializations
        ]

    def update(
        self,
        specialization_id: uuid.UUID,
        request: SpecializationUpdateRequest,
    ) -> SpecializationResponse:
        specialization = self._get_specialization(specialization_id)

        if request.department_id is not None:
            self._validate_department(request.department_id)

        if request.name is not None:
            department_id = (
                request.department_id
                if request.department_id is not None
                else specialization.department_id
            )

            self._check_duplicate_name(
                department_id=department_id,
                name=request.name,
                exclude_specialization_id=specialization.id,
            )

        update_data = request.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(specialization, field, value)

        specialization = self.specialization_repository.update(
            specialization
        )

        return SpecializationResponse.model_validate(specialization)

    def delete(
        self,
        specialization_id: uuid.UUID,
    ) -> SpecializationResponse:
        specialization = self._get_specialization(specialization_id)

        if specialization.status == SpecializationStatusEnum.INACTIVE:
            raise SpecializationAlreadyInactiveException()

        specialization.status = SpecializationStatusEnum.INACTIVE

        specialization = self.specialization_repository.update(
            specialization
        )

        return SpecializationResponse.model_validate(specialization)

    # ==========================================================
    # Private Methods
    # ==========================================================

    def _get_specialization(
        self,
        specialization_id: uuid.UUID,
    ) -> Specialization:
        specialization = self.specialization_repository.get_by_id(
            specialization_id
        )

        if specialization is None:
            raise SpecializationNotFoundException()

        return specialization

    def _validate_department(
        self,
        department_id: uuid.UUID,
    ) -> None:
        department = self.department_repository.get_by_id(department_id)

        if department is None:
            raise DepartmentNotFoundException()

    def _check_duplicate_name(
        self,
        department_id: uuid.UUID,
        name: str,
        exclude_specialization_id: uuid.UUID | None = None,
    ) -> None:
        specialization = (
            self.specialization_repository.get_by_department_and_name(
                department_id,
                name,
            )
        )

        if specialization is None:
            return

        if (
            exclude_specialization_id is not None
            and specialization.id == exclude_specialization_id
        ):
            return

        raise SpecializationAlreadyExistsException()

    def _build_specialization(
        self,
        request: SpecializationCreateRequest,
    ) -> Specialization:
        return Specialization(
            department_id=request.department_id,
            name=request.name,
            description=request.description,
        )