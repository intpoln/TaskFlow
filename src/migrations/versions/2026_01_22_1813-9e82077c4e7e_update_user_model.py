"""update user model

Revision ID: 9e82077c4e7e
Revises: eb463cdceff0
Create Date: 2026-01-22 18:13:52.087178

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9e82077c4e7e"
down_revision: Union[str, Sequence[str], None] = "eb463cdceff0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "users",
        "username",
        existing_type=sa.VARCHAR(length=30),
        type_=sa.String(length=128),
        existing_nullable=False,
    )
    op.drop_constraint(op.f("users_github_id_key"), "users", type_="unique")
    op.drop_constraint(op.f("users_username_key"), "users", type_="unique")
    op.drop_column("users", "github_id")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "users", sa.Column("github_id", sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    )
    op.create_unique_constraint(
        op.f("users_username_key"), "users", ["username"], postgresql_nulls_not_distinct=False
    )
    op.create_unique_constraint(
        op.f("users_github_id_key"), "users", ["github_id"], postgresql_nulls_not_distinct=False
    )
    op.alter_column(
        "users",
        "username",
        existing_type=sa.String(length=128),
        type_=sa.VARCHAR(length=30),
        existing_nullable=False,
    )
