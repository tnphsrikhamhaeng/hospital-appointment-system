"""add image url to departments

Revision ID: 9f401486b70d
Revises: 86b13ac615e7
Create Date: 2026-09-12 15:25:02.081052

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9f401486b70d'
down_revision: Union[str, Sequence[str], None] = '86b13ac615e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "departments",
        sa.Column("image_url", sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("departments", "image_url")