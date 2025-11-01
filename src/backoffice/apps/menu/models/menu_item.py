from typing import Dict, List, Optional

from sqlalchemy import (Boolean, CheckConstraint, ForeignKey, Index, Integer,
                        String, Text)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backoffice.models import Base, CreatedUpdatedMixin, IdMixin


class MenuItem(Base, IdMixin, CreatedUpdatedMixin):
    __tablename__ = "menu_items"
    __repr_fields__ = ("slug", "name", "category_id")

    slug: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    grams: Mapped[int] = mapped_column(Integer, nullable=False)
    kilocalories: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    proteins: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fats: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    carbohydrated: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # If the element belongs to a company (not a template), indicate the owner
    owner_company_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Relationships
    category: Mapped["Category"] = relationship(  # type: ignore
        back_populates="items", passive_deletes=True
    )
    owner_company: Mapped[Optional["Company"]] = relationship("Company")  # type: ignore
    images: Mapped[List["MenuImage"]] = relationship(  # type: ignore
        "MenuImage", back_populates="menu_item", cascade="all, delete-orphan"
    )
    branch_menus: Mapped[List["CompanyBranchMenu"]] = relationship(  # type: ignore
        back_populates="menu_item",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("grams > 0", name="ck_menu_item_grams_pos"),
        CheckConstraint(
            "kilocalories IS NULL OR kilocalories > 0",
            name="ck_menu_item_kilocalories_pos",
        ),
        CheckConstraint(
            "proteins IS NULL OR proteins > 0", name="ck_menu_item_proteins_pos"
        ),
        CheckConstraint("fats IS NULL OR fats > 0", name="ck_menu_item_fats_pos"),
        CheckConstraint(
            "carbohydrated IS NULL OR carbohydrated > 0",
            name="ck_menu_item_carbohydrated_pos",
        ),
        Index("ck_menu_item_category_slug", "category_id", "slug"),
        CheckConstraint(
            "(is_template = TRUE AND owner_company_id IS NULL) OR (is_template = FALSE AND owner_company_id IS NOT NULL)",
            name="ck_menu_item_template_owner_consistency",
        ),
    )

    @property
    def breadcrumbs(self) -> List[Dict[str, str]]:
        crumbs: List[Dict[str, str]] = []
        node = self.category
        while node is not None:
            crumbs.insert(0, {"name": str(node.name), "slug": str(node.slug)})
            node = node.parent
        return crumbs
