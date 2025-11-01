from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.menu.models import MenuItem
from src.backoffice.apps.menu.repositories import MenuItemRepository
from src.backoffice.apps.menu.schemas import MenuItemCreate, MenuItemUpdate
from src.backoffice.core.services import SlugService


class MenuItemService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = MenuItemRepository(session)

    async def create(self, menu_item_data: MenuItemCreate) -> MenuItem:
        menu_item_data_dict = menu_item_data.model_dump()
        menu_item_data_dict["slug"] = ""

        menu_item = await self.repository.create(**menu_item_data_dict)

        SlugService.set_slug(instance=menu_item, name=menu_item.name)
        await self.session.flush()

        return menu_item

    async def get_by_slug(self, slug: str) -> Optional[MenuItem]:
        return await self.repository.get_by_slug(slug)

    async def list(
        self,
        category_id: Optional[int] = None,
    ) -> List[MenuItem]:
        return await self.repository.list_with_optional_category(
            category_id=category_id,
        )

    async def update_by_slug(
        self, menu_item_slug: str, update_data: MenuItemUpdate
    ) -> Optional[MenuItem]:
        update_dict = update_data.model_dump(exclude_unset=True)
        updated_item = await self.repository.update_by_slug(
            menu_item_slug, **update_dict
        )

        if updated_item and "name" in update_dict:
            SlugService.set_slug(instance=updated_item, name=str(updated_item.name))
            await self.session.flush()

        return updated_item

    async def delete_by_slug(self, menu_item_slug: str) -> bool:
        return await self.repository.delete_by_slug(menu_item_slug)

    async def get_templates(self) -> List[MenuItem]:
        return await self.repository.get_templates()
