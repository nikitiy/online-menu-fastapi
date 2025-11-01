from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backoffice.models.base import Base
from src.backoffice.models.mixins import CreatedUpdatedMixin, IdMixin


class OAuthAccount(Base, IdMixin, CreatedUpdatedMixin):
    __tablename__ = "oauth_accounts"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    provider: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # google, yandex, vk
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_username: Mapped[Optional[str]] = mapped_column(String(255))
    provider_email: Mapped[Optional[str]] = mapped_column(String(255))
    access_token: Mapped[Optional[str]] = mapped_column(Text)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True)
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="oauth_accounts")  # type: ignore
