from datetime import datetime

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.database import Base


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(60), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(60), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    tasks: Mapped[list[int] | None] = mapped_column(ForeignKey('tasks.id'), default=None)
