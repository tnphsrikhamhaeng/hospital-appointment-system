from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import UserRoleEnum, UserStatusEnum
from app.models.user import User




class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user: User,
    ) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def get_by_id(
        self,
        user_id: uuid.UUID,
    ) -> User | None:
        statement = select(User).where(
            User.id == user_id,
        )

        return self.db.scalar(statement)

    def get_by_username(
        self,
        username: str,
    ) -> User | None:
        statement = select(User).where(
            User.username == username,
        )

        return self.db.scalar(statement)

    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        statement = select(User).where(
            User.email == email,
        )

        return self.db.scalar(statement)

    def get_by_email_and_role(
        self,
        email: str,
        role: UserRoleEnum,
    ) -> User | None:
        statement = select(User).where(
            User.email == email,
            User.role == role,
        )

        return self.db.scalar(statement)

    def get_by_phone_number(
        self,
        phone_number: str,
    ) -> User | None:
        statement = select(User).where(
            User.phone_number == phone_number,
        )

        return self.db.scalar(statement)

    def get_by_phone_number_and_role(
        self,
        phone_number: str,
        role: UserRoleEnum,
    ) -> User | None:
        statement = select(User).where(
            User.phone_number == phone_number,
            User.role == role,
        )

        return self.db.scalar(statement)
    
    def list_staff(
        self,
        status: UserStatusEnum | None = None,
        search: str | None = None,
    ) -> list[User]:
        statement = select(User).where(
            User.role == UserRoleEnum.HOSPITAL_STAFF,
        )

        if status is not None:
            statement = statement.where(
                User.status == status,
            )

        if search:
            search_value = f"%{search.strip()}%"

            statement = statement.where(
                (
                    User.username.ilike(search_value)
                    | User.first_name.ilike(search_value)
                    | User.last_name.ilike(search_value)
                    | User.email.ilike(search_value)
                )
            )

        statement = statement.order_by(
            User.created_at.desc(),
        )

        return list(
            self.db.scalars(statement).all()
        )

    def update(
        self,
        user: User,
    ) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user