from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backoffice.models.base import Base
from src.backoffice.models.mixins import CreatedUpdatedMixin, IdMixin


class RefreshToken(Base, IdMixin, CreatedUpdatedMixin):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")  # type: ignore
