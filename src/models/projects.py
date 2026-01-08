from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.database import Base


class ProjectOrm(Base):
    __tablename__ = "projects"

    __table_args__ = (
        UniqueConstraint('owner_id', 'title', name='unique_project_title'),
        UniqueConstraint('id', 'owner_id', name='uc_project_id_owner'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column(nullable=True, default=None)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())