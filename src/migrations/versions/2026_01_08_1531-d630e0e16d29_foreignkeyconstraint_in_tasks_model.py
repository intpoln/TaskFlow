"""ForeignKeyConstraint in tasks model

Revision ID: d630e0e16d29
Revises: c4460bcdd55b
Create Date: 2026-01-08 15:31:29.465683

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d630e0e16d29"
down_revision: Union[str, Sequence[str], None] = "c4460bcdd55b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint("uc_project_id_owner", "projects", ["id", "owner_id"])
    op.drop_constraint(op.f("tasks_project_id_fkey"), "tasks", type_="foreignkey")
    op.create_foreign_key(
        "fk_task_project_owner", "tasks", "projects", ["project_id", "owner_id"], ["id", "owner_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_task_project_owner", "tasks", type_="foreignkey")
    op.create_foreign_key(
        op.f("tasks_project_id_fkey"), "tasks", "projects", ["project_id"], ["id"]
    )
    op.drop_constraint("uc_project_id_owner", "projects", type_="unique")
