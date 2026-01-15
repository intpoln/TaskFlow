"""Updated constraints, on delete actions

Revision ID: 066f17fbaa53
Revises: eca0aa94ff3b
Create Date: 2026-01-15 11:46:35.158818

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "066f17fbaa53"
down_revision: Union[str, Sequence[str], None] = "eca0aa94ff3b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(op.f("projects_owner_id_fkey"), "projects", type_="foreignkey")
    op.create_foreign_key(None, "projects", "users", ["owner_id"], ["id"], ondelete="CASCADE")
    op.alter_column("tasks", "description", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column(
        "tasks",
        "status",
        existing_type=postgresql.ENUM("TODO", "IN_PROGRESS", "DONE", name="task_status"),
        nullable=True,
    )
    op.drop_constraint(op.f("fk_task_project_owner"), "tasks", type_="foreignkey")
    op.drop_constraint(op.f("tasks_owner_id_fkey"), "tasks", type_="foreignkey")
    op.create_foreign_key(None, "tasks", "users", ["owner_id"], ["id"], ondelete="CASCADE")
    op.create_foreign_key(
        "fk_task_project_owner",
        "tasks",
        "projects",
        ["project_id", "owner_id"],
        ["id", "owner_id"],
        ondelete="CASCADE",
    )
    op.alter_column(
        "users",
        "username",
        existing_type=sa.VARCHAR(length=60),
        type_=sa.String(length=30),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users",
        "username",
        existing_type=sa.String(length=30),
        type_=sa.VARCHAR(length=60),
        existing_nullable=False,
    )
    op.drop_constraint("fk_task_project_owner", "tasks", type_="foreignkey")
    op.drop_constraint(None, "tasks", type_="foreignkey")
    op.create_foreign_key(op.f("tasks_owner_id_fkey"), "tasks", "users", ["owner_id"], ["id"])
    op.create_foreign_key(
        op.f("fk_task_project_owner"),
        "tasks",
        "projects",
        ["project_id", "owner_id"],
        ["id", "owner_id"],
    )
    op.alter_column(
        "tasks",
        "status",
        existing_type=postgresql.ENUM("TODO", "IN_PROGRESS", "DONE", name="task_status"),
        nullable=False,
    )
    op.alter_column("tasks", "description", existing_type=sa.VARCHAR(), nullable=False)
    op.drop_constraint(None, "projects", type_="foreignkey")
    op.create_foreign_key(op.f("projects_owner_id_fkey"), "projects", "users", ["owner_id"], ["id"])
