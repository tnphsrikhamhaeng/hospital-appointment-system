"""scope user contact uniqueness by role

Revision ID: 86b13ac615e7
Revises: eff06a5dfc3a
Create Date: 2026-09-06 15:27:52.572269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "86b13ac615e7"
down_revision: Union[str, Sequence[str], None] = "eff06a5dfc3a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "users_email_key",
        "users",
        type_="unique",
    )

    op.drop_constraint(
        "users_phone_number_key",
        "users",
        type_="unique",
    )

    op.create_unique_constraint(
        "uq_users_email_role",
        "users",
        ["email", "role"],
    )

    op.create_unique_constraint(
        "uq_users_phone_role",
        "users",
        ["phone_number", "role"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_users_email_role",
        "users",
        type_="unique",
    )

    op.drop_constraint(
        "uq_users_phone_role",
        "users",
        type_="unique",
    )

    op.create_unique_constraint(
        "users_email_key",
        "users",
        ["email"],
    )

    op.create_unique_constraint(
        "users_phone_number_key",
        "users",
        ["phone_number"],
    )