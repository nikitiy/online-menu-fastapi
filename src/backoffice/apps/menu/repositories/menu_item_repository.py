from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.backoffice.apps.menu.models import Category, MenuItem
from src.backoffice.core.repositories import BaseRepository


class MenuItemRepository(BaseRepository[MenuItem]):
    def __init__(self, session: AsyncSession):
        super().__init__(MenuItem, session)

    async def get_by_slug(self, slug: str) -> Optional[MenuItem]:
        result = await self.session.execute(
            select(MenuItem).where(MenuItem.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_by_slug_with_relations(self, slug: str) -> Optional[MenuItem]:
        """Load menu item with images and category with parent chain"""
        result = await self.session.execute(
            select(MenuItem)
            .where(MenuItem.slug == slug)
            .options(
                selectinload(MenuItem.images),
                selectinload(MenuItem.category).selectinload(Category.parent),
            )
        )
        menu_item = result.scalar_one_or_none()
        if menu_item and menu_item.category:
            # Load full parent chain recursively
            await self._load_category_parent_chain(menu_item.category)
        return menu_item

    async def get_by_id_with_relations(self, item_id: int) -> Optional[MenuItem]:
        """Load menu item by ID with images and category with parent chain"""
        result = await self.session.execute(
            select(MenuItem)
            .where(MenuItem.id == item_id)
            .options(
                selectinload(MenuItem.images),
                selectinload(MenuItem.category).selectinload(Category.parent),
            )
        )
        menu_item = result.scalar_one_or_none()
        if menu_item and menu_item.category:
            # Load full parent chain recursively
            await self._load_category_parent_chain(menu_item.category)
        return menu_item

    async def _load_category_parent_chain(self, category: Category) -> None:
        """Recursively load parent category chain"""
        if category.parent_id is None:
            return

        # Load parent if not already loaded
        if category.parent is None:
            result = await self.session.execute(
                select(Category)
                .where(Category.id == category.parent_id)
                .options(selectinload(Category.parent))
            )
            category.parent = result.scalar_one_or_none()

        # Recursively load parent's parent chain
        if category.parent:
            await self._load_category_parent_chain(category.parent)

    async def update_by_slug(self, slug: str, **kwargs) -> Optional[MenuItem]:
        menu_item = await self.get_by_slug(slug)
        if not menu_item:
            return None

        update_data = {k: v for k, v in kwargs.items() if v is not None}
        if not update_data:
            return menu_item

        for field, value in update_data.items():
            if hasattr(menu_item, field):
                setattr(menu_item, field, value)

        await self.session.flush()
        await self.session.refresh(menu_item)
        return menu_item

    async def delete_by_slug(self, slug: str) -> bool:
        menu_item = await self.get_by_slug(slug)
        if not menu_item:
            return False

        await self.session.delete(menu_item)
        await self.session.flush()
        return True

    async def get_by_category(
        self, category_id: int, skip: int = 0, limit: int = 100
    ) -> List[MenuItem]:
        result = await self.session.execute(
            select(MenuItem)
            .where(MenuItem.category_id == category_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_templates(self, skip: int = 0, limit: int = 100) -> List[MenuItem]:
        result = await self.session.execute(
            select(MenuItem)
            .where(MenuItem.is_template == True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_with_optional_category(
        self,
        category_slug: Optional[str] = None,
    ) -> List[MenuItem]:
        stmt = select(MenuItem).options(
            selectinload(MenuItem.images),
            selectinload(MenuItem.category).selectinload(Category.parent),
        )

        if category_slug is not None:
            stmt = stmt.join(Category, MenuItem.category_id == Category.id).where(
                Category.slug == category_slug
            )

        stmt = stmt.order_by(MenuItem.created_at.desc())

        result = await self.session.execute(stmt)
        menu_items = list(result.scalars().all())

        # Load parent chains for all categories
        for menu_item in menu_items:
            if menu_item.category:
                await self._load_category_parent_chain(menu_item.category)

        return menu_items
