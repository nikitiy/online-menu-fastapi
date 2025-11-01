from datetime import datetime, timezone

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backoffice.models import Base, IdMixin


class GeocodingResult(Base, IdMixin):
    __tablename__ = "geocoding_results"
    __repr_fields__ = ("provider", "query")
    __repr_maxlen__ = 60

    query: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True, index=True)
    formatted_address: Mapped[str] = mapped_column(Text, nullable=True)
    country: Mapped[str] = mapped_column(String(255), nullable=True)
    region: Mapped[str] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(255), nullable=True)
    street: Mapped[str] = mapped_column(String(255), nullable=True)
    house_number: Mapped[str] = mapped_column(String(50), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=True)
    place_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    place_type: Mapped[str] = mapped_column(String(100), nullable=True)
    accuracy: Mapped[str] = mapped_column(
        String(50), nullable=True
    )  # ROOFTOP, RANGE_INTERPOLATED, GEOMETRIC_CENTER, APPROXIMATE
    confidence: Mapped[float] = mapped_column(Float, nullable=True)  # 0.0 - 1.0
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # External ID for integration
    external_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    raw_response: Mapped[str] = mapped_column(Text, nullable=True)
    is_successful: Mapped[bool] = mapped_column(default=True, nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    address_id: Mapped[int] = mapped_column(
        ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    address: Mapped["Address"] = relationship("Address")  # type: ignore
