from typing import List

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backoffice.models import Base, IdMixin


class Region(Base, IdMixin):
    __tablename__ = "regions"
    __repr_fields__ = ("name", "country_id")

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(20), nullable=True, index=True)
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    country: Mapped["Country"] = relationship("Country", back_populates="regions")  # type: ignore
    cities: Mapped[List["City"]] = relationship(  # type: ignore
        "City", back_populates="region", cascade="all, delete-orphan"
    )
