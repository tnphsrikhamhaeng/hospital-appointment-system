from __future__ import annotations

import uuid

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.enums import DoctorStatusEnum, UserRoleEnum, UserStatusEnum
from app.core.exceptions import (
    DepartmentNotFoundException,
    DoctorEmailAlreadyExistsException,
    DoctorLicenseAlreadyExistsException,
    DoctorNotFoundException,
    DoctorPhoneNumberAlreadyExistsException,
    InvalidCredentialsException,
    SpecializationNotFoundException,
    UsernameAlreadyExistsException,
)
from app.models.doctor import Doctor
from app.models.doctor_specialization import DoctorSpecialization
from app.models.user import User
from app.repositories.department_repository import DepartmentRepository
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.specialization_repository import (
    SpecializationRepository,
)
from app.repositories.user_repository import UserRepository
from app.schemas.doctor import (
    DoctorCreateRequest,
    DoctorDeactivateRequest,
    DoctorResponse,
    DoctorUpdateRequest,
)
from app.utils.security import hash_password, verify_password


class DoctorService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.doctor_repository = DoctorRepository(db)
        self.department_repository = DepartmentRepository(db)
        self.specialization_repository = SpecializationRepository(db)

    def create_doctor(
        self,
        request: DoctorCreateRequest,
    ) -> DoctorResponse:

        try:
            if self.user_repository.get_by_username(request.employee_id):
                raise UsernameAlreadyExistsException()

            if self.user_repository.get_by_email_and_role(
                request.email,
                UserRoleEnum.DOCTOR,
            ):
                raise DoctorEmailAlreadyExistsException()

            if self.user_repository.get_by_phone_number_and_role(
                request.phone_number,
                UserRoleEnum.DOCTOR,
            ):
                raise DoctorPhoneNumberAlreadyExistsException()

            if self.doctor_repository.get_by_license_number(
                request.license_number,
            ):
                raise DoctorLicenseAlreadyExistsException()

            if self.doctor_repository.get_by_email(request.email):
                raise DoctorEmailAlreadyExistsException()

            if self.doctor_repository.get_by_phone_number(request.phone_number):
                raise DoctorPhoneNumberAlreadyExistsException()

            department = self.department_repository.get_by_id(
                request.department_id,
            )

            if department is None:
                raise DepartmentNotFoundException()

            specializations = self.specialization_repository.get_by_ids(
                request.specialization_ids,
            )

            if len(specializations) != len(request.specialization_ids):
                raise SpecializationNotFoundException()

            user = User(
                username=request.employee_id,
                first_name=request.first_name,
                last_name=request.last_name,
                phone_number=request.phone_number,
                email=request.email,
                password=hash_password(request.password),
                role=UserRoleEnum.DOCTOR,
                status=UserStatusEnum.ACTIVE,
                gender=None,
                date_of_birth=None,
            )

            user = self.user_repository.create(user)

            doctor = Doctor(
                user_id=user.id,
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

            self.db.commit()
            self.db.refresh(doctor)

            return DoctorResponse.model_validate(doctor)

        except Exception:
            self.db.rollback()
            raise

    def get_doctors(
        self,
        department_id: uuid.UUID | None = None,
        status: DoctorStatusEnum | None = None,
        search: str | None = None,
    ) -> list[Doctor]:
        if status is None and not search:
            status = DoctorStatusEnum.ACTIVE

        return self.doctor_repository.get_doctors(
            department_id=department_id,
            status=status,
            search=search,
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
            raise DoctorNotFoundException()

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
            raise DoctorNotFoundException()

        update_data = request.model_dump(
            exclude_unset=True,
        )

        # profile_image_url เป็น HttpUrl จาก Pydantic
        # ต้องแปลงเป็น string ก่อนส่งเข้า SQLAlchemy
        if "profile_image_url" in update_data:
            update_data["profile_image_url"] = (
                str(update_data["profile_image_url"])
                if update_data["profile_image_url"]
                else None
            )

        if "email" in update_data:
            existing_doctor = self.doctor_repository.get_by_email(
                update_data["email"],
            )

            if existing_doctor is not None and existing_doctor.id != doctor.id:
                raise DoctorEmailAlreadyExistsException()

        if "phone_number" in update_data:
            existing_doctor = self.doctor_repository.get_by_phone_number(
                update_data["phone_number"],
            )

            if existing_doctor is not None and existing_doctor.id != doctor.id:
                raise DoctorPhoneNumberAlreadyExistsException()

        if "department_id" in update_data:
            department = self.department_repository.get_by_id(
                update_data["department_id"],
            )

            if department is None:
                raise DepartmentNotFoundException()

        specializations = None

        if "specialization_ids" in update_data:
            specializations = self.specialization_repository.get_by_ids(
                update_data["specialization_ids"],
            )

            if len(specializations) != len(update_data["specialization_ids"]):
                raise SpecializationNotFoundException()

            update_data.pop("specialization_ids")

        for key, value in update_data.items():
            setattr(doctor, key, value)

        if specializations is not None:
            self.db.execute(
                delete(DoctorSpecialization).where(
                    DoctorSpecialization.doctor_id == doctor.id
                )
            )

            self.db.flush()

            self.db.expire(
                doctor,
                [
                    "doctor_specializations",
                    "specializations",
                ],
            )

            for specialization in specializations:
                doctor.doctor_specializations.append(
                    DoctorSpecialization(
                        specialization_id=specialization.id,
                    )
                )

        doctor = self.doctor_repository.update(doctor)

        return DoctorResponse.model_validate(doctor)

    def delete_doctor(
        self,
        doctor_id: uuid.UUID,
        request: DoctorDeactivateRequest,
        current_user: User,
    ) -> DoctorResponse:

        doctor = self.doctor_repository.get_by_id(
            doctor_id=doctor_id,
            status=DoctorStatusEnum.ACTIVE,
        )

        if doctor is None:
            raise DoctorNotFoundException()

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

        doctor.status = DoctorStatusEnum.INACTIVE

        doctor = self.doctor_repository.update(doctor)

        return DoctorResponse.model_validate(doctor)