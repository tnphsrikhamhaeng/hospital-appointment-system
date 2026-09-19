"""allow cancelled appointment slot reuse

Revision ID: ca4b80f13ec4
Revises: eb4bfbee1bbb
Create Date: 2026-09-03 21:16:04.503804

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ca4b80f13ec4"
down_revision: Union[str, Sequence[str], None] = "eb4bfbee1bbb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.drop_constraint(
        "uq_appointments_doctor_date_start_time",
        "appointments",
        type_="unique",
    )

    op.create_index(
        "uq_appointments_doctor_date_start_time_active",
        "appointments",
        [
            "doctor_id",
            "appointment_date",
            "start_time",
        ],
        unique=True,
        postgresql_where=sa.text(
            "status != 'cancelled'"
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "uq_appointments_doctor_date_start_time_active",
        table_name="appointments",
    )

    op.create_unique_constraint(
        "uq_appointments_doctor_date_start_time",
        "appointments",
        [
            "doctor_id",
            "appointment_date",
            "start_time",
        ],
    )