import uuid

from fastapi import HTTPException, status

from app.core.enums import DepartmentStatusEnum
from app.models.department import Department
from app.repositories.department_repository import DepartmentRepository
from app.schemas.department import (DepartmentCreateRequest,
                                    DepartmentResponse,
                                    DepartmentUpdateRequest)


class DepartmentService:
    def __init__(self, repository: DepartmentRepository):
        self.repository = repository

    def create_department(
        self,
        request: DepartmentCreateRequest,
    ) -> DepartmentResponse:
        existing_department = self.repository.get_by_name(request.name)
        
        if existing_department:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department already exists.",
            )

        department = Department(
            name=request.name,
            description=request.description,
            slot_duration_minutes=request.slot_duration_minutes,
            status=DepartmentStatusEnum.ACTIVE,
        )

        department = self.repository.create(department)

        return DepartmentResponse.model_validate(department)

    def get_department(
        self,
        department_id: uuid.UUID,
    ) -> DepartmentResponse:
        department = self.repository.get_by_id(department_id)

        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found.",
            )

        return DepartmentResponse.model_validate(department)

    def list_departments(self) -> list[DepartmentResponse]:
        departments = self.repository.get_all()

        return [
            DepartmentResponse.model_validate(department) for department in departments
        ]

    def update_department(
        self,
        department_id: uuid.UUID,
        request: DepartmentUpdateRequest,
    ) -> DepartmentResponse:
        department = self.repository.get_by_id(department_id)

        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found.",
            )

        if request.name is not None and request.name != department.name:
            existing_department = self.repository.get_by_name(request.name)

            if existing_department and existing_department.id != department.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Department already exists.",
                )

        update_data = request.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(department, field, value)

        department = self.repository.update(department)

        return DepartmentResponse.model_validate(department)

    def delete_department(
        self,
        department_id: uuid.UUID,
    ) -> DepartmentResponse:
        department = self.repository.get_by_id(department_id)

        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found.",
            )

        if department.status == DepartmentStatusEnum.INACTIVE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department is already inactive.",
            )

        department.status = DepartmentStatusEnum.INACTIVE

        department = self.repository.update(department)

        return DepartmentResponse.model_validate(department)
