from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, func, UniqueConstraint, ForeignKeyConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

from src.database import Base


class TaskStatus(str, Enum):
    TODO = 'TODO'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = "DONE"


task_status_enum = PgEnum(TaskStatus, name='task_status', create_type=False)


class TaskOrm(Base):
    __tablename__ = "tasks"

    __table_args__ = (
        UniqueConstraint('project_id', 'title', name='unique_project_task.title'),
        ForeignKeyConstraint(
            ['project_id', 'owner_id'],
            ['projects.id', 'projects.owner_id'],
            name='fk_task_project_owner'
        )
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    status: Mapped[TaskStatus] = mapped_column(
        task_status_enum,
        nullable=False,
        default=TaskStatus.TODO
    )
    category_id: Mapped[int | None] = mapped_column(ForeignKey('categories.id'), default=None)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    notify: Mapped[bool] = mapped_column(default=False)
    project_id: Mapped[int | None] = mapped_column(default=None)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
