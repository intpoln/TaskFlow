"""updated users, added categories, tasks

Revision ID: 859a5e965e1a
Revises: 4675022e110d
Create Date: 2026-01-04 13:23:24.947887

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "859a5e965e1a"
down_revision: Union[str, Sequence[str], None] = "4675022e110d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(op.f("users_tasks_fkey"), "users", type_="foreignkey")
    op.drop_column("users", "tasks")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("users", sa.Column("tasks", sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(op.f("users_tasks_fkey"), "users", "tasks", ["tasks"], ["id"])
