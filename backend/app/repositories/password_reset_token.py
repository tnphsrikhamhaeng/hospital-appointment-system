from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        reset_token: PasswordResetToken,
    ) -> PasswordResetToken:
        self.db.add(reset_token)
        self.db.flush()
        return reset_token

    def get_by_token(
        self,
        token: str,
    ) -> PasswordResetToken | None:
        statement = select(PasswordResetToken).where(
            PasswordResetToken.token == token,
        )

        return self.db.scalar(statement)

    def mark_as_used(
        self,
        reset_token: PasswordResetToken,
    ) -> PasswordResetToken:
        reset_token.used_at = datetime.now(timezone.utc)

        self.db.add(reset_token)
        self.db.flush()
        self.db.refresh(reset_token)

        return reset_token