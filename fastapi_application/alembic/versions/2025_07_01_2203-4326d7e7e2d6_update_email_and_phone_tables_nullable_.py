"""update email and phone tables nullable is true for user

Revision ID: 4326d7e7e2d6
Revises: 41bbb5992e6c
Create Date: 2025-07-01 22:03:29.469934

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4326d7e7e2d6"
down_revision: Union[str, None] = "41bbb5992e6c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "phone_number",
        existing_type=sa.VARCHAR(length=10),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "phone_number",
        existing_type=sa.VARCHAR(length=10),
        nullable=False,
    )
