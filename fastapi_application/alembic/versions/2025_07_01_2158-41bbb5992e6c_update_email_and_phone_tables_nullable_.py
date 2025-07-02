"""update email and phone tables nullable is true for user

Revision ID: 41bbb5992e6c
Revises: 7d00cdc70e6f
Create Date: 2025-07-01 21:58:43.051736

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "41bbb5992e6c"
down_revision: Union[str, None] = "7d00cdc70e6f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("users", "email", existing_type=sa.VARCHAR(length=40), nullable=True)


def downgrade() -> None:
    op.alter_column("users", "email", existing_type=sa.VARCHAR(length=40), nullable=False)
