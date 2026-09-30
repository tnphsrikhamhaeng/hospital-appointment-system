"""add medical record created notification type

Revision ID: 67de49c318c5
Revises: 1208983e4567
Create Date: 2026-09-29 22:08:23.200761

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "67de49c318c5"
down_revision: Union[str, Sequence[str], None] = "1208983e4567"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TYPE notificationtypeenum
        ADD VALUE IF NOT EXISTS 'medical_record_created'
        """
    )


def downgrade() -> None:
    pass