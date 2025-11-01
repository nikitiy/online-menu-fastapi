from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backoffice.models import Base, IdMixin


class Street(Base, IdMixin):
    __tablename__ = "streets"
    __repr_fields__ = ("name", "city_id")

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    city_id: Mapped[int] = mapped_column(
        ForeignKey("cities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Street center
    latitude: Mapped[float] = mapped_column(Float, nullable=True, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True, index=True)
    # Street, avenue, alley, etc.
    street_type: Mapped[str] = mapped_column(String(50), nullable=True)

    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    city: Mapped["City"] = relationship("City", back_populates="streets")  # type: ignore
    addresses: Mapped[list["Address"]] = relationship(  # type: ignore
        "Address", back_populates="street", cascade="all, delete-orphan"
    )
