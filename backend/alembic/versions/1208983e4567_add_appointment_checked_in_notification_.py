"""add appointment checked in notification type

Revision ID: 1208983e4567
Revises: 3fb79319c1e9
Create Date: 2026-09-29 21:42:45.838978

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "1208983e4567"
down_revision: Union[str, Sequence[str], None] = "3fb79319c1e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TYPE notificationtypeenum
        ADD VALUE IF NOT EXISTS 'appointment_checked_in'
        """
    )


def downgrade() -> None:
    pass