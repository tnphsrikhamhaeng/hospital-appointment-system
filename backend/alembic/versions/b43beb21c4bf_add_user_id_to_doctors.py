"""add user id to doctors

Revision ID: b43beb21c4bf
Revises: 6d7653ee10aa
Create Date: 2026-09-06 15:06:11.277046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b43beb21c4bf'
down_revision: Union[str, Sequence[str], None] = '6d7653ee10aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "doctors",
        sa.Column(
            "user_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_doctors_user_id",
        "doctors",
        "users",
        ["user_id"],
        ["id"],
    )

    op.create_unique_constraint(
        "uq_doctors_user_id",
        "doctors",
        ["user_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_doctors_user_id",
        "doctors",
        type_="unique",
    )

    op.drop_constraint(
        "fk_doctors_user_id",
        "doctors",
        type_="foreignkey",
    )

    op.drop_column(
        "doctors",
        "user_id",
    )