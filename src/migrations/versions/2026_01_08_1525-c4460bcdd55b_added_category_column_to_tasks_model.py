"""added category column to tasks model

Revision ID: c4460bcdd55b
Revises: 5b954c85e565
Create Date: 2026-01-08 15:25:38.579907

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4460bcdd55b"
down_revision: Union[str, Sequence[str], None] = "5b954c85e565"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("tasks", sa.Column("category_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "tasks", "categories", ["category_id"], ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "tasks", type_="foreignkey")
    op.drop_column("tasks", "category_id")
