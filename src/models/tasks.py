from datetime import datetime

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class UserOrm(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str]
    category = Mapped[int] = mapped_column(ForeignKey("categories.id"))
    date_from: Mapped[datetime | None] = mapped_column(default=None)
    date_to: Mapped[datetime | None] = mapped_column(default=None)
