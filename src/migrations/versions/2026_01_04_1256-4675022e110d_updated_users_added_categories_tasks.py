"""updated users, added categories, tasks

Revision ID: 4675022e110d
Revises: 010e237ccd69
Create Date: 2026-01-04 12:56:36.682182

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4675022e110d"
down_revision: Union[str, Sequence[str], None] = "010e237ccd69"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("category", sa.Integer(), nullable=False),
        sa.Column("date_from", sa.DateTime(), nullable=True),
        sa.Column("date_to", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category"],
            ["categories.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("users", sa.Column("tasks", sa.Integer(), nullable=True))
    op.create_unique_constraint(None, "users", ["hashed_password"])
    op.create_foreign_key(None, "users", "tasks", ["tasks"], ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "users", type_="foreignkey")
    op.drop_constraint(None, "users", type_="unique")
    op.drop_column("users", "tasks")
    op.drop_table("tasks")
    op.drop_table("categories")
