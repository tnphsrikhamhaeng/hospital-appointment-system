"""allow null personnel profile fields

Revision ID: eff06a5dfc3a
Revises: b43beb21c4bf
Create Date: 2026-09-06 15:18:52.119500

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eff06a5dfc3a'
down_revision: Union[str, Sequence[str], None] = 'b43beb21c4bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "users",
        "gender",
        existing_type=sa.Enum(
            "MALE",
            "FEMALE",
            "OTHER",
            name="gender_enum",
        ),
        nullable=True,
    )

    op.alter_column(
        "users",
        "date_of_birth",
        existing_type=sa.Date(),
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users",
        "date_of_birth",
        existing_type=sa.Date(),
        nullable=False,
    )

    op.alter_column(
        "users",
        "gender",
        existing_type=sa.Enum(
            "MALE",
            "FEMALE",
            "OTHER",
            name="gender_enum",
        ),
        nullable=False,
    )
