from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.database import Base


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(60), unique=True)
    hashed_password: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    telegram_id: Mapped[int | None] = mapped_column(nullable=True, default=None)
    telegram_username: Mapped[str | None] = mapped_column(nullable=True, default=None)
    is_superuser: Mapped[bool] = mapped_column(default=False)
