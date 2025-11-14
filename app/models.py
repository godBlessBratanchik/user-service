from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class Profile(Base):
    """Модель профиля пользователя"""
    __tablename__ = "profiles"

    user_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True, default=None)
    bio: Mapped[Optional[str]] = mapped_column(String, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<Profile(user_id={self.user_id}, email={self.email})>"
