from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

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

    def get_by_phone_number(
        self,
        phone_number: str,
    ) -> User | None:
        statement = select(User).where(
            User.phone_number == phone_number,
        )

        return self.db.scalar(statement)