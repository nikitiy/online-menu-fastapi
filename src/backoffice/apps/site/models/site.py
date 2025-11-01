from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backoffice.models import Base, IdMixin


class Site(IdMixin, Base):
    __tablename__ = "sites"

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # Relationships
    company: Mapped["Company"] = relationship(  # type: ignore
        "src.backoffice.apps.company.models.Company",
        back_populates="site",
    )
