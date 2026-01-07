"""Model categories - name column renamed to title

Revision ID: ffca91da5cf0
Revises: e145a8f8e2c2
Create Date: 2026-01-06 17:43:02.721767

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffca91da5cf0'
down_revision: Union[str, Sequence[str], None] = 'e145a8f8e2c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('categories', sa.Column('title', sa.String(), nullable=False))
    op.drop_constraint(op.f('categories_name_key'), 'categories', type_='unique')
    op.create_unique_constraint(None, 'categories', ['title'])
    op.drop_column('categories', 'name')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('categories', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'categories', type_='unique')
    op.create_unique_constraint(op.f('categories_name_key'), 'categories', ['name'], postgresql_nulls_not_distinct=False)
    op.drop_column('categories', 'title')
