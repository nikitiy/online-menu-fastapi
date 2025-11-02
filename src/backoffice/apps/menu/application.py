from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.menu.models import MenuItem
from src.backoffice.apps.menu.schemas import MenuItemCreate, MenuItemUpdate
from src.backoffice.apps.menu.services import MenuImageService, MenuItemService
from src.backoffice.core.services.s3_client import s3_client


class MenuApplication:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.menu_item_service = MenuItemService(session)
        self.menu_image_service = MenuImageService(session)

    async def get_menu_item_by_slug(self, slug: str) -> Optional[MenuItem]:
        menu_item = await self.menu_item_service.get_by_slug_with_relations(slug)
        if menu_item:
            await self._add_urls_to_images(menu_item)
        return menu_item

    async def list_menu_items(
        self, category_id: Optional[int] = None
    ) -> List[MenuItem]:
        menu_items = await self.menu_item_service.list(category_id=category_id)
        # Add URLs to images for all menu items
        for menu_item in menu_items:
            await self._add_urls_to_images(menu_item)
        return menu_items

    async def create_menu_item(self, menu_item_data: MenuItemCreate) -> MenuItem:
        menu_item = await self.menu_item_service.create(menu_item_data)
        await self.session.commit()
        # Reload with relations after commit
        menu_item = await self.menu_item_service.get_by_id_with_relations(menu_item.id)
        if not menu_item:
            raise ValueError("Menu item not found after creation")
        # Add URLs to images
        await self._add_urls_to_images(menu_item)
        return menu_item

    async def update_menu_item(
        self, menu_item_slug: str, update_data: MenuItemUpdate
    ) -> Optional[MenuItem]:
        menu_item = await self.menu_item_service.update_by_slug(
            menu_item_slug, update_data
        )
        if not menu_item:
            return None
        await self.session.commit()
        # Reload with relations after commit
        menu_item = await self.menu_item_service.get_by_slug_with_relations(
            menu_item_slug
        )
        if menu_item:
            await self._add_urls_to_images(menu_item)
        return menu_item

    async def delete_menu_item(self, menu_item_slug: str) -> bool:
        result = await self.menu_item_service.delete_by_slug(menu_item_slug)
        await self.session.commit()
        return result

    async def add_image_to_menu_item(
        self,
        menu_item_slug: str,
        file: UploadFile,
        alt_text: Optional[str] = None,
        is_primary: bool = False,
        display_order: int = 0,
    ) -> MenuItem:
        menu_item = await self.menu_item_service.get_by_slug(menu_item_slug)
        if not menu_item:
            raise ValueError("Menu item not found")

        await self.menu_image_service.upload_image(
            menu_item_id=menu_item.id,
            file=file,
            alt_text=alt_text,
            is_primary=is_primary,
            display_order=display_order,
        )
        await self.session.commit()
        menu_item = await self.menu_item_service.get_by_slug_with_relations(
            menu_item_slug
        )
        if menu_item:
            await self._add_urls_to_images(menu_item)
        return menu_item

    async def remove_image_from_menu_item(
        self, menu_item_slug: str, image_id: int
    ) -> MenuItem:
        await self.menu_image_service.delete_image(image_id)
        await self.session.commit()
        menu_item = await self.menu_item_service.get_by_slug_with_relations(
            menu_item_slug
        )
        if not menu_item:
            raise ValueError("Menu item not found")
        await self._add_urls_to_images(menu_item)
        return menu_item

    async def set_primary_image_for_menu_item(
        self, menu_item_slug: str, image_id: int
    ) -> MenuItem:
        await self.menu_image_service.set_primary_image(image_id)
        await self.session.commit()
        menu_item = await self.menu_item_service.get_by_slug_with_relations(
            menu_item_slug
        )
        if not menu_item:
            raise ValueError("Menu item not found")
        await self._add_urls_to_images(menu_item)
        return menu_item

    async def _add_urls_to_images(self, menu_item: MenuItem) -> None:
        """Add URL attribute to all images in menu item"""
        if menu_item.images:
            for image in menu_item.images:
                image.url = await s3_client.get_presigned_url(image.file_path, 24)
