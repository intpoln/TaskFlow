"""user model superuser column added

Revision ID: e145a8f8e2c2
Revises: 1c7fc995f658
Create Date: 2026-01-05 22:57:11.791348

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e145a8f8e2c2"
down_revision: Union[str, Sequence[str], None] = "1c7fc995f658"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users", sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false")
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "is_superuser")
