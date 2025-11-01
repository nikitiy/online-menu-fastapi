from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.menu.models import MenuImage
from src.backoffice.core.repositories import BaseRepository


class MenuImageRepository(BaseRepository[MenuImage]):
    def __init__(self, session: AsyncSession):
        super().__init__(MenuImage, session)

    async def get_by_menu_item(
        self, menu_item_id: int, active_only: bool = True
    ) -> List[MenuImage]:
        stmt = select(MenuImage).where(MenuImage.menu_item_id == menu_item_id)
        if active_only:
            stmt = stmt.where(MenuImage.is_active == True)
        stmt = stmt.order_by(MenuImage.display_order, MenuImage.updated_at)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_primary_image(self, menu_item_id: int) -> Optional[MenuImage]:
        result = await self.session.execute(
            select(MenuImage).where(
                MenuImage.menu_item_id == menu_item_id,
                MenuImage.is_primary == True,
                MenuImage.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    async def unset_primary_images(self, menu_item_id: int) -> None:
        images = await self.session.execute(
            select(MenuImage).where(
                MenuImage.menu_item_id == menu_item_id,
                MenuImage.is_primary == True,
            )
        )
        for image in images.scalars().all():
            image.is_primary = False
        await self.session.flush()
