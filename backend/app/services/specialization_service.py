import uuid

from fastapi import HTTPException, status

from app.core.enums import SpecializationStatusEnum
from app.models.specialization import Specialization
from app.repositories.department_repository import DepartmentRepository
from app.repositories.specialization_repository import SpecializationRepository
from app.schemas.specialization import (SpecializationCreateRequest,
                                        SpecializationResponse,
                                        SpecializationUpdateRequest)


class SpecializationService:
    def __init__(
        self,
        specialization_repository: SpecializationRepository,
        department_repository: DepartmentRepository,
    ):
        self.specialization_repository = specialization_repository
        self.department_repository = department_repository

    def create_specialization(
        self,
        request: SpecializationCreateRequest,
    ) -> SpecializationResponse:

        department = self.department_repository.get_by_id(request.department_id)

        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found.",
            )

        existing_specialization = (
            self.specialization_repository.get_by_department_and_name(
                request.department_id,
                request.name,
            )
        )

        if existing_specialization:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Specialization already exists.",
            )

        specialization = Specialization(
            department_id=request.department_id,
            name=request.name,
            description=request.description,
        )

        specialization = self.specialization_repository.create(specialization)

        return SpecializationResponse.model_validate(specialization)

    def get_specialization(
        self,
        specialization_id: uuid.UUID,
    ) -> SpecializationResponse:

        specialization = self.specialization_repository.get_by_id(specialization_id)

        if not specialization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specialization not found.",
            )

        return SpecializationResponse.model_validate(specialization)

    def list_specializations(
        self,
    ) -> list[SpecializationResponse]:

        specializations = self.specialization_repository.get_all()

        return [SpecializationResponse.model_validate(s) for s in specializations]

    def update_specialization(
        self,
        specialization_id: uuid.UUID,
        request: SpecializationUpdateRequest,
    ) -> SpecializationResponse:

        specialization = self.specialization_repository.get_by_id(specialization_id)

        if not specialization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specialization not found.",
            )

        if request.name is not None:
            department_id = (
                request.department_id
                if request.department_id is not None
                else specialization.department_id
            )

            existing_specialization = (
                self.specialization_repository.get_by_department_and_name(
                    department_id,
                    request.name,
                )
            )

            if (
                existing_specialization
                and existing_specialization.id != specialization.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Specialization already exists.",
                )
        update_data = request.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(specialization, field, value)

        specialization = self.specialization_repository.update(specialization)

        return SpecializationResponse.model_validate(specialization)

    def delete_specialization(
        self,
        specialization_id: uuid.UUID,
    ) -> SpecializationResponse:

        specialization = self.specialization_repository.get_by_id(specialization_id)

        if not specialization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specialization not found.",
            )

        if specialization.status == SpecializationStatusEnum.INACTIVE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Specialization is already inactive.",
            )

        specialization.status = SpecializationStatusEnum.INACTIVE

        specialization = self.specialization_repository.update(specialization)

        return SpecializationResponse.model_validate(specialization)
