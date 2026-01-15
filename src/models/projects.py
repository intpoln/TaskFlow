"""ORM модель проекта.

Содержит модель ProjectOrm для группировки задач в проекты.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.database import Base


class ProjectOrm(Base):
    """Модель проекта в базе данных.

    Проекты позволяют группировать связанные задачи.
    Каждый пользователь имеет свои проекты.

    Attributes:
        id: Уникальный идентификатор проекта.
        title: Название проекта (до 40 символов).
        description: Описание проекта (опционально, до 512 символов).
        owner_id: ID владельца проекта (FK на users).
        created_at: Дата и время создания.

    Constraints:
        unique_project_title: Один пользователь не может иметь два проекта
            с одинаковым названием.
        uc_project_id_owner: Составной ключ для FK из tasks.
    """

    __tablename__ = "projects"

    __table_args__ = (
        UniqueConstraint("owner_id", "title", name="unique_project_title"),
        UniqueConstraint("id", "owner_id", name="uc_project_id_owner"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True, default=None)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
