from __future__ import annotations
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import DoctorStatusEnum
from app.models.doctor import Doctor
from app.models.doctor_specialization import DoctorSpecialization
from app.repositories.department_repository import DepartmentRepository
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.specialization_repository import (
    SpecializationRepository,
)

from app.schemas.doctor import (
    DoctorCreateRequest,
    DoctorResponse,
    DoctorUpdateRequest
)


class DoctorService:
    def __init__(self, db: Session):
        self.db = db

        self.doctor_repository = DoctorRepository(db)
        self.department_repository = DepartmentRepository(db)
        self.specialization_repository = (
            SpecializationRepository(db)
        )

    def create_doctor(
        self,
        request: DoctorCreateRequest,
    ) -> DoctorResponse:

        if self.doctor_repository.get_by_license_number(
            request.license_number
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="License number already exists.",
            )

        if self.doctor_repository.get_by_email(
            request.email
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists.",
            )

        if self.doctor_repository.get_by_phone_number(
            request.phone_number
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number already exists.",
            )

        department = self.department_repository.get_by_id(
            request.department_id
        )

        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found.",
            )

        specializations = (
            self.specialization_repository.get_by_ids(
                request.specialization_ids
            )
        )

        if len(specializations) != len(
            request.specialization_ids
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more specializations not found.",
            )

        doctor = Doctor(
            profile_image_url=(
                str(request.profile_image_url)
                if request.profile_image_url
                else None
            ),
            preface=request.preface,
            first_name=request.first_name,
            last_name=request.last_name,
            license_number=request.license_number,
            phone_number=request.phone_number,
            email=request.email,
            status=DoctorStatusEnum.ACTIVE,
            department_id=request.department_id,
        )

        for specialization in specializations:
            doctor.doctor_specializations.append(
                DoctorSpecialization(
                    specialization_id=specialization.id,
                )
            )

        doctor = self.doctor_repository.create(doctor)

        return DoctorResponse.model_validate(doctor)
    
    def get_doctors(self) -> list[Doctor]:
        return self.doctor_repository.get_doctors(
            status=DoctorStatusEnum.ACTIVE,
        )
    
    def get_doctor_by_id(
        self,
        doctor_id: uuid.UUID,
    ) -> Doctor:
        doctor = self.doctor_repository.get_by_id(
            doctor_id=doctor_id,
            status=DoctorStatusEnum.ACTIVE,
        )

        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found.",
            )

        return doctor
    
    def update_doctor(
        self,
        doctor_id: uuid.UUID,
        request: DoctorUpdateRequest,
    ) -> DoctorResponse:

        doctor = self.doctor_repository.get_by_id(
            doctor_id=doctor_id,
        )

        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found.",
            )

        update_data = request.model_dump(
            exclude_unset=True,
        )
        
        if "email" in update_data:
            existing_doctor = self.doctor_repository.get_by_email(
                update_data["email"],
            )

            if (
                existing_doctor is not None
                and existing_doctor.id != doctor.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists.",
                )
        
        if "phone_number" in update_data:
            existing_doctor = self.doctor_repository.get_by_phone_number(
                update_data["phone_number"],
            )
            if (
                existing_doctor is not None
                and existing_doctor.id != doctor.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Phone number already exists.",
                )
        
        if "department_id" in update_data:
            department = self.department_repository.get_by_id(
                update_data["department_id"],
            )

            if department is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Department not found.",
                )
                
        update_data = request.model_dump(
            exclude_unset=True,
        )

        specializations = None

        if "specialization_ids" in update_data:
            specializations = self.specialization_repository.get_by_ids(
                update_data["specialization_ids"],
            )

            if len(specializations) != len(update_data["specialization_ids"]):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="One or more specializations not found.",
                )

            update_data.pop("specialization_ids")

        for key, value in update_data.items():
            setattr(doctor, key, value)

        if specializations is not None:
            doctor.specializations = specializations

        doctor = self.doctor_repository.update(doctor)

        return DoctorResponse.model_validate(doctor)
    
    def delete_doctor(
        self,
        doctor_id: uuid.UUID,
    ) -> DoctorResponse:

        doctor = self.doctor_repository.get_by_id(
            doctor_id=doctor_id,
            status=DoctorStatusEnum.ACTIVE,
        )

        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found.",
            )

        doctor.status = DoctorStatusEnum.INACTIVE

        doctor = self.doctor_repository.update(doctor)

        return DoctorResponse.model_validate(doctor)