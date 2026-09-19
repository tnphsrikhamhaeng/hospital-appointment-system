"""add appointment rescheduled notification type

Revision ID: 6d7653ee10aa
Revises: 760e843f8763
Create Date: 2026-09-04 20:45:35.742516

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '6d7653ee10aa'
down_revision: Union[str, Sequence[str], None] = '760e843f8763'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        ALTER TYPE notificationtypeenum
        ADD VALUE IF NOT EXISTS 'appointment_rescheduled'
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass