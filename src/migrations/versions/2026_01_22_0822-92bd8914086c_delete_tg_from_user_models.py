"""delete tg from user models

Revision ID: 92bd8914086c
Revises: 066f17fbaa53
Create Date: 2026-01-22 08:22:44.893471

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "92bd8914086c"
down_revision: Union[str, Sequence[str], None] = "066f17fbaa53"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("users", "telegram_username")
    op.drop_column("users", "telegram_id")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "users", sa.Column("telegram_id", sa.INTEGER(), autoincrement=False, nullable=True)
    )
    op.add_column(
        "users", sa.Column("telegram_username", sa.VARCHAR(), autoincrement=False, nullable=True)
    )
