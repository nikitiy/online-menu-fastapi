from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backoffice.models import Base, IdMixin


class City(Base, IdMixin):
    __tablename__ = "cities"
    __repr_fields__ = ("name", "country_id", "region_id")

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"), nullable=False, index=True
    )
    region_id: Mapped[int] = mapped_column(
        ForeignKey("regions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=True, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True, index=True)
    population: Mapped[int] = mapped_column(Integer, nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    country: Mapped["Country"] = relationship("Country", back_populates="cities")  # type: ignore
    region: Mapped["Region"] = relationship("Region", back_populates="cities")  # type: ignore
    streets: Mapped[list["Street"]] = relationship(  # type: ignore
        "Street", back_populates="city", cascade="all, delete-orphan"
    )
