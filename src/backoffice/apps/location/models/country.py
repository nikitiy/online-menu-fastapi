from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backoffice.models import Base, IdMixin


class Country(Base, IdMixin):
    __tablename__ = "countries"
    __repr_fields__ = ("name", "code")

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    code: Mapped[str] = mapped_column(
        String(3), nullable=False, unique=True, index=True
    )  # ISO 3166-1 alpha-3
    code_alpha2: Mapped[str] = mapped_column(
        String(2), nullable=False, unique=True, index=True
    )  # ISO 3166-1 alpha-2
    phone_code: Mapped[str] = mapped_column(String(10), nullable=True)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    regions: Mapped[list["Region"]] = relationship(  # type: ignore
        "Region", back_populates="country", cascade="all, delete-orphan"
    )
    cities: Mapped[list["City"]] = relationship(  # type: ignore
        "City", back_populates="country", cascade="all, delete-orphan"
    )
