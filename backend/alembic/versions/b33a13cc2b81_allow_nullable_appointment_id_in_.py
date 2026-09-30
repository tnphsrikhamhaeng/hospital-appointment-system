"""allow nullable appointment id in notification logs

Revision ID: b33a13cc2b81
Revises: aoc_20260914
Create Date: 2026-09-29 20:59:45.024783

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b33a13cc2b81"
down_revision: Union[str, Sequence[str], None] = "aoc_20260914"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "notification_logs",
        "appointment_id",
        existing_type=sa.UUID(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "notification_logs",
        "appointment_id",
        existing_type=sa.UUID(),
        nullable=False,
    )