"""change appointment qr token length

Revision ID: 760e843f8763
Revises: 3ee4f5746e56
Create Date: 2026-09-04 17:43:42.802901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '760e843f8763'
down_revision: Union[str, Sequence[str], None] = '3ee4f5746e56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Keep the existing VARCHAR(36) length so existing
    # UUID-based QR tokens remain valid.
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass