"""updated models

Revision ID: 1c7fc995f658
Revises: 859a5e965e1a
Create Date: 2026-01-04 21:26:30.708253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '1c7fc995f658'
down_revision: Union[str, Sequence[str], None] = '859a5e965e1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    task_status_enum = sa.Enum(
        'TODO',
        'IN_PROGRESS',
        'DONE',
        name='task_status'
    )
    task_status_enum.create(op.get_bind())
    """Upgrade schema."""
    op.create_table('projects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('tasks', sa.Column('title', sa.String(), nullable=False))
    op.add_column('tasks', sa.Column('status', task_status_enum, nullable=False))
    op.add_column('tasks', sa.Column('deadline', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('notify', sa.Boolean(), nullable=False))
    op.add_column('tasks', sa.Column('project_id', sa.Integer(), nullable=False))
    op.add_column('tasks', sa.Column('user_id', sa.Integer(), nullable=False))
    op.add_column('tasks', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.drop_constraint(op.f('tasks_category_fkey'), 'tasks', type_='foreignkey')
    op.create_foreign_key(None, 'tasks', 'projects', ['project_id'], ['id'])
    op.create_foreign_key(None, 'tasks', 'users', ['user_id'], ['id'])
    op.drop_column('tasks', 'date_to')
    op.drop_column('tasks', 'category')
    op.drop_column('tasks', 'date_from')
    op.add_column('users', sa.Column('telegram_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('telegram_username', sa.String(), nullable=True))
    op.drop_constraint(op.f('users_hashed_password_key'), 'users', type_='unique')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_unique_constraint(op.f('users_hashed_password_key'), 'users', ['hashed_password'], postgresql_nulls_not_distinct=False)
    op.drop_column('users', 'telegram_username')
    op.drop_column('users', 'telegram_id')
    op.add_column('tasks', sa.Column('date_from', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('tasks', sa.Column('category', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('tasks', sa.Column('date_to', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.create_foreign_key(op.f('tasks_category_fkey'), 'tasks', 'categories', ['category'], ['id'])
    op.drop_column('tasks', 'updated_at')
    op.drop_column('tasks', 'user_id')
    op.drop_column('tasks', 'project_id')
    op.drop_column('tasks', 'notify')
    op.drop_column('tasks', 'deadline')
    op.drop_column('tasks', 'status')
    sa.Enum(name='task_status_enum').drop(op.get_bind())
    op.drop_column('tasks', 'title')
    op.drop_table('projects')