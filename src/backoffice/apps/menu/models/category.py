from typing import List

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backoffice.models import Base, IdMixin


class Category(IdMixin, Base):
    __tablename__ = "categories"
    __repr_fields__ = ("slug", "parent_id")

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Relationships
    parent: Mapped["Category | None"] = relationship(
        remote_side="Category.id", back_populates="children", passive_deletes=True
    )
    children: Mapped["Category | None"] = relationship(
        back_populates="parent", cascade="all, delete-orphan", single_parent=True
    )
    items: Mapped[List["MenuItem"]] = relationship(  # type: ignore
        "MenuItem",
        back_populates="category",
        cascade="all, delete-orphan",
    )

    __table_args__ = (Index("ix_categories_parent_id_slug", "parent_id", "slug"),)
