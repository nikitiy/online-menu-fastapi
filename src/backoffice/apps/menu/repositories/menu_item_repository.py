from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.menu.models import MenuItem
from src.backoffice.core.repositories import BaseRepository


class MenuItemRepository(BaseRepository[MenuItem]):
    def __init__(self, session: AsyncSession):
        super().__init__(MenuItem, session)

    async def get_by_slug(self, slug: str) -> Optional[MenuItem]:
        result = await self.session.execute(
            select(MenuItem).where(MenuItem.slug == slug)
        )
        return result.scalar_one_or_none()

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
        category_id: Optional[int] = None,
    ) -> List[MenuItem]:
        stmt = select(MenuItem)

        if category_id is not None:
            stmt = stmt.where(MenuItem.category_id == category_id)

        stmt = stmt.order_by(MenuItem.created_at.desc())

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
