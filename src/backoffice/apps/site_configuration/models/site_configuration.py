from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from src.backoffice.models import Base, SingletonMixin


class SiteConfiguration(SingletonMixin, Base):
    __tablename__ = "site_configuration"

    site_name: Mapped[str] = mapped_column(String(255), nullable=False)
    maintenance_mode: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
