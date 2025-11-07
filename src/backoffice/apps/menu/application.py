from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.services import CompanyService
from src.backoffice.apps.menu.models import MenuItem
from src.backoffice.apps.menu.schemas import MenuItemCreate, MenuItemUpdate
from src.backoffice.apps.menu.services import MenuImageService, MenuItemService
from src.backoffice.core.access.access_control import CompanyAccessControl
from src.backoffice.core.access.permissions import (
    MenuItemPermission,
    check_menu_item_permission,
)
from src.backoffice.core.services.s3_client import s3_client


class MenuApplication:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.menu_item_service = MenuItemService(session)
        self.menu_image_service = MenuImageService(session)
        self.company_service = CompanyService(session)
        self.access_control = CompanyAccessControl(session)

    async def get_menu_item_by_slug(self, slug: str, user_id: int) -> MenuItem:
        menu_item = await self.menu_item_service.get_by_slug_with_relations_or_raise(
            slug
        )
        await self.access_control.check_resource_permission(
            resource_company_id=menu_item.owner_company_id,
            user_id=user_id,
            permission=MenuItemPermission.READ,
            permission_checker=check_menu_item_permission,
        )
        await self._add_urls_to_images(menu_item)
        return menu_item

    async def get_company_menu_items(
        self,
        company_subdomain: str,
        user_id: int,
    ) -> List[MenuItem]:
        company = await self.company_service.get_by_subdomain_or_raise(
            company_subdomain
        )
        await self.access_control.check_company_permission(
            company_id=company.id,
            user_id=user_id,
            permission=MenuItemPermission.READ,
            permission_checker=check_menu_item_permission,
        )
        menu_items = await self.menu_item_service.list_by_company(company_id=company.id)
        for menu_item in menu_items:
            await self._add_urls_to_images(menu_item)
        return menu_items

    async def create_menu_item(
        self, menu_item_data: MenuItemCreate, user_id: int
    ) -> MenuItem:
        company = await self.company_service.get_by_subdomain_or_raise(
            menu_item_data.company_subdomain
        )
        await self.access_control.check_company_permission(
            company_id=company.id,
            user_id=user_id,
            permission=MenuItemPermission.CREATE,
            permission_checker=check_menu_item_permission,
        )

        menu_item = await self.menu_item_service.create(menu_item_data)
        await self.session.commit()
        menu_item = await self.menu_item_service.get_by_id_with_relations_or_raise(
            menu_item.id
        )

        await self._add_urls_to_images(menu_item)
        return menu_item

    async def update_menu_item(
        self, menu_item_slug: str, update_data: MenuItemUpdate, user_id: int
    ) -> MenuItem:
        menu_item = await self.menu_item_service.get_by_slug_or_raise(menu_item_slug)
        await self.access_control.check_resource_permission(
            resource_company_id=menu_item.owner_company_id,
            user_id=user_id,
            permission=MenuItemPermission.UPDATE,
            permission_checker=check_menu_item_permission,
        )

        await self.menu_item_service.update_by_slug_or_raise(
            menu_item_slug, update_data
        )
        await self.session.commit()
        menu_item = await self.menu_item_service.get_by_slug_with_relations_or_raise(
            menu_item_slug
        )
        await self._add_urls_to_images(menu_item)
        return menu_item

    async def delete_menu_item(self, menu_item_slug: str, user_id: int) -> None:
        menu_item = await self.menu_item_service.get_by_slug_or_raise(menu_item_slug)
        await self.access_control.check_resource_permission(
            resource_company_id=menu_item.owner_company_id,
            user_id=user_id,
            permission=MenuItemPermission.DELETE,
            permission_checker=check_menu_item_permission,
        )
        await self.menu_item_service.delete_by_slug_or_raise(menu_item_slug)
        await self.session.commit()

    async def add_image_to_menu_item(
        self,
        menu_item_slug: str,
        file: UploadFile,
        user_id: int,
        alt_text: Optional[str] = None,
        is_primary: bool = False,
        display_order: int = 0,
    ) -> MenuItem:
        menu_item = await self.menu_item_service.get_by_slug_or_raise(menu_item_slug)
        await self.access_control.check_resource_permission(
            resource_company_id=menu_item.owner_company_id,
            user_id=user_id,
            permission=MenuItemPermission.UPDATE,
            permission_checker=check_menu_item_permission,
        )

        await self.menu_image_service.upload_image(
            menu_item_id=menu_item.id,
            file=file,
            alt_text=alt_text,
            is_primary=is_primary,
            display_order=display_order,
        )
        await self.session.commit()
        menu_item = await self.menu_item_service.get_by_slug_with_relations_or_raise(
            menu_item_slug
        )
        await self._add_urls_to_images(menu_item)
        return menu_item

    async def remove_image_from_menu_item(
        self, menu_item_slug: str, image_id: int, user_id: int
    ) -> MenuItem:
        menu_item = await self.menu_item_service.get_by_slug_or_raise(menu_item_slug)
        await self.access_control.check_resource_permission(
            resource_company_id=menu_item.owner_company_id,
            user_id=user_id,
            permission=MenuItemPermission.UPDATE,
            permission_checker=check_menu_item_permission,
        )

        await self.menu_image_service.delete_image(image_id)
        await self.session.commit()
        menu_item = await self.menu_item_service.get_by_slug_with_relations_or_raise(
            menu_item_slug
        )
        await self._add_urls_to_images(menu_item)
        return menu_item

    async def set_primary_image_for_menu_item(
        self, menu_item_slug: str, image_id: int, user_id: int
    ) -> MenuItem:
        menu_item = await self.menu_item_service.get_by_slug_or_raise(menu_item_slug)
        await self.access_control.check_resource_permission(
            resource_company_id=menu_item.owner_company_id,
            user_id=user_id,
            permission=MenuItemPermission.UPDATE,
            permission_checker=check_menu_item_permission,
        )

        await self.menu_image_service.set_primary_image(image_id)
        await self.session.commit()
        menu_item = await self.menu_item_service.get_by_slug_with_relations_or_raise(
            menu_item_slug
        )
        await self._add_urls_to_images(menu_item)
        return menu_item

    @staticmethod
    async def _add_urls_to_images(menu_item: MenuItem) -> None:
        if menu_item.images:
            for image in menu_item.images:
                image.url = await s3_client.get_presigned_url(image.file_path, 24)
