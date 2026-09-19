"""add appointment overlap constraints

Revision ID: add_appointment_overlap_constraints
Revises: 9f401486b70d
Create Date: 2026-09-14
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "add_appointment_overlap_constraints"
down_revision: Union[str, Sequence[str], None] = "9f401486b70d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable GiST support for UUID/text equality operators.
    op.execute(
        "CREATE EXTENSION IF NOT EXISTS btree_gist"
    )

    # Remove the old constraint because it only prevents
    # identical start times and also blocks cancelled appointments.
    op.execute(
        """
        ALTER TABLE appointments
        DROP CONSTRAINT IF EXISTS
        uq_appointments_doctor_date_start_time
        """
    )

    # Prevent overlapping appointments for the same doctor.
    # Cancelled appointments are excluded from the constraint.
    op.execute(
        """
        ALTER TABLE appointments
        ADD CONSTRAINT ex_appointments_doctor_time_overlap
        EXCLUDE USING gist (
            doctor_id WITH =,
            appointment_date WITH =,
            tsrange(
                (appointment_date + start_time),
                (appointment_date + end_time),
                '[)'
            ) WITH &&
        )
        WHERE (status <> 'cancelled')
        """
    )

    # Prevent overlapping appointments for the same patient,
    # even when the appointments are with different doctors.
    # Cancelled appointments are excluded from the constraint.
    op.execute(
        """
        ALTER TABLE appointments
        ADD CONSTRAINT ex_appointments_patient_time_overlap
        EXCLUDE USING gist (
            patient_id WITH =,
            appointment_date WITH =,
            tsrange(
                (appointment_date + start_time),
                (appointment_date + end_time),
                '[)'
            ) WITH &&
        )
        WHERE (status <> 'cancelled')
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE appointments
        DROP CONSTRAINT IF EXISTS
        ex_appointments_patient_time_overlap
        """
    )

    op.execute(
        """
        ALTER TABLE appointments
        DROP CONSTRAINT IF EXISTS
        ex_appointments_doctor_time_overlap
        """
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