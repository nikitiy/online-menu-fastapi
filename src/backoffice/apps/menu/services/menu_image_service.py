from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.menu.models import MenuImage
from src.backoffice.apps.menu.repositories import (
    MenuImageRepository,
    MenuItemRepository,
)
from src.backoffice.core.exceptions import NotFoundError
from src.backoffice.core.services.s3_client import s3_client


class MenuImageService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = MenuImageRepository(session)
        self.menu_item_repository = MenuItemRepository(session)

    async def upload_image(
        self,
        menu_item_id: int,
        file: UploadFile,
        alt_text: Optional[str] = None,
        is_primary: bool = False,
        display_order: int = 0,
    ) -> MenuImage:
        menu_item = await self.menu_item_repository.get_by_id(menu_item_id)
        if not menu_item:
            raise NotFoundError(f"Menu item with id {menu_item_id} not found")

        upload_result = await s3_client.upload_file(file, folder="menu-images")

        if is_primary:
            await self.repository.unset_primary_images(menu_item_id)

        menu_image_data = {
            "filename": upload_result["filename"],
            "original_filename": upload_result["original_filename"],
            "file_path": upload_result["file_path"],
            "file_size": upload_result["file_size"],
            "mime_type": upload_result["mime_type"],
            "width": upload_result.get("width"),
            "height": upload_result.get("height"),
            "alt_text": alt_text,
            "menu_item_id": menu_item_id,
            "display_order": display_order,
            "is_primary": is_primary,
            "is_active": True,
        }

        menu_image = await self.repository.create(**menu_image_data)
        return await self._add_url_to_image(menu_image)

    async def get_images_by_menu_item(self, menu_item_id: int) -> List[MenuImage]:
        images = await self.repository.get_by_menu_item(menu_item_id, active_only=True)
        return [await self._add_url_to_image(image) for image in images]

    async def get_primary_image(self, menu_item_id: int) -> Optional[MenuImage]:
        image = await self.repository.get_primary_image(menu_item_id)
        if image:
            return await self._add_url_to_image(image)
        return None

    async def update_image(
        self,
        image_id: int,
        alt_text: Optional[str] = None,
        is_primary: Optional[bool] = None,
        display_order: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> MenuImage:
        image = await self.repository.get_by_id(image_id)
        if not image:
            raise NotFoundError(f"Image with id {image_id} not found")

        if is_primary and not image.is_primary:
            await self.repository.unset_primary_images(image.menu_item_id)

        update_data = {}
        if alt_text is not None:
            update_data["alt_text"] = alt_text
        if is_primary is not None:
            update_data["is_primary"] = is_primary
        if display_order is not None:
            update_data["display_order"] = display_order
        if is_active is not None:
            update_data["is_active"] = is_active

        for field, value in update_data.items():
            if hasattr(image, field):
                setattr(image, field, value)
        await self.session.flush()
        await self.session.refresh(image)

        return await self._add_url_to_image(image)

    async def delete_image(self, image_id: int) -> bool:
        image = await self.repository.get_by_id(image_id)
        if not image:
            return False

        await s3_client.delete_file(image.file_path)

        if image.file_path:
            thumbnail_path = image.file_path.replace(
                "menu-images/", "menu-images/thumbnails/"
            )
            await s3_client.delete_file(thumbnail_path)

        return await self.repository.delete(image_id)

    async def set_primary_image(self, image_id: int) -> MenuImage:
        image = await self.repository.get_by_id(image_id)
        if not image:
            raise NotFoundError(f"Image with id {image_id} not found")

        await self.repository.unset_primary_images(image.menu_item_id)

        image.is_primary = True
        await self.session.flush()
        await self.session.refresh(image)

        return await self._add_url_to_image(image)

    async def get_presigned_url(self, image_id: int, expiry_hours: int = 1) -> str:
        image = await self.repository.get_by_id(image_id)
        if not image:
            raise NotFoundError(f"Image with id {image_id} not found")

        return await s3_client.get_presigned_url(image.file_path, expiry_hours)

    @staticmethod
    async def _add_url_to_image(image: MenuImage) -> MenuImage:
        image.url = await s3_client.get_presigned_url(image.file_path, 24)
        return image
