from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.enums import (
    DepartmentStatusEnum,
    DoctorStatusEnum,
    SpecializationStatusEnum,
    UserRoleEnum,
    UserStatusEnum,
)
from app.core.exceptions import (
    DepartmentNotFoundException,
    DoctorNotFoundException,
    SpecializationNotFoundException,
)
from app.models.department import Department
from app.models.doctor import Doctor
from app.models.specialization import Specialization
from app.models.user import User
from app.repositories.department_repository import DepartmentRepository
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.specialization_repository import (
    SpecializationRepository,
)
from app.schemas.reactivate import (
    ReactivateRequest,
    ReactivateTargetType,
)
from app.utils.security import verify_password
from app.repositories.user_repository import UserRepository


class ReactivateService:
    def __init__(self, db: Session):
        self.db = db

        self.department_repository = DepartmentRepository(db)
        self.doctor_repository = DoctorRepository(db)
        self.specialization_repository = SpecializationRepository(db)
        self.user_repository = UserRepository(db)

    def reactivate(
        self,
        request: ReactivateRequest,
        current_user: User,
    ):
        if not verify_password(
            request.password,
            current_user.password,
        ):
            raise ValueError("รหัสผ่านไม่ถูกต้อง")

        if request.target_type == ReactivateTargetType.DOCTOR:
            return self._reactivate_doctor(request.target_id)

        if request.target_type == ReactivateTargetType.DEPARTMENT:
            return self._reactivate_department(request.target_id)

        if request.target_type == ReactivateTargetType.SPECIALIZATION:
            return self._reactivate_specialization(
                request.target_id
            )

        if request.target_type == ReactivateTargetType.STAFF:
            return self._reactivate_staff(
                request.target_id
            )

        raise ValueError("ไม่รองรับประเภทข้อมูลนี้")

    def _reactivate_doctor(
        self,
        doctor_id: uuid.UUID,
    ) -> Doctor:
        doctor = self.doctor_repository.get_by_id(
            doctor_id=doctor_id,
        )

        if doctor is None:
            raise DoctorNotFoundException()

        if doctor.status != DoctorStatusEnum.INACTIVE:
            raise ValueError("Doctor นี้ยังไม่ได้ถูกปิดใช้งาน")

        doctor.status = DoctorStatusEnum.ACTIVE

        doctor = self.doctor_repository.update(doctor)

        return doctor

    def _reactivate_department(
        self,
        department_id: uuid.UUID,
    ) -> Department:
        department = self.department_repository.get_by_id(
            department_id,
        )

        if department is None:
            raise DepartmentNotFoundException()

        if department.status != DepartmentStatusEnum.INACTIVE:
            raise ValueError("Department นี้ยังไม่ได้ถูกปิดใช้งาน")

        department.status = DepartmentStatusEnum.ACTIVE

        department = self.department_repository.update(department)

        return department

    def _reactivate_specialization(
        self,
        specialization_id: uuid.UUID,
    ) -> Specialization:
        specialization = self.specialization_repository.get_by_id(
            specialization_id,
        )

        if specialization is None:
            raise SpecializationNotFoundException()

        if specialization.status != SpecializationStatusEnum.INACTIVE:
            raise ValueError("Specialization นี้ยังไม่ได้ถูกปิดใช้งาน")

        specialization.status = SpecializationStatusEnum.ACTIVE

        specialization = self.specialization_repository.update(
            specialization,
        )

        return specialization
    
    def _reactivate_staff(
        self,
        staff_id: uuid.UUID,
    ) -> User:
        staff = self.user_repository.get_by_id(
            staff_id,
        )

        if staff is None or staff.role != UserRoleEnum.HOSPITAL_STAFF:
            raise ValueError("ไม่พบ Staff")

        if staff.status != UserStatusEnum.INACTIVE:
            raise ValueError(
                "Staff นี้ยังไม่ได้ถูกปิดใช้งาน"
            )

        staff.status = UserStatusEnum.ACTIVE

        staff = self.user_repository.update(
            staff,
        )

        return staff