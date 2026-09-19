"""create notification settings

Revision ID: 3ee4f5746e56
Revises: ca4b80f13ec4
Create Date: 2026-09-04 16:06:33.120158

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3ee4f5746e56"
down_revision: Union[str, Sequence[str], None] = "ca4b80f13ec4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "notification_settings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("all_notifications", sa.Boolean(), nullable=False),
        sa.Column(
            "appointment_notifications",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "medical_record_notifications",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "system_notifications",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("notification_settings")