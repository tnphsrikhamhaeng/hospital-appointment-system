"""add system announcement notification type

Revision ID: 3fb79319c1e9
Revises: b33a13cc2b81
Create Date: 2026-09-29 21:08:15.240044

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "3fb79319c1e9"
down_revision: Union[str, Sequence[str], None] = "b33a13cc2b81"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TYPE notificationtypeenum
        ADD VALUE IF NOT EXISTS 'system_announcement'
        """
    )


def downgrade() -> None:
    pass