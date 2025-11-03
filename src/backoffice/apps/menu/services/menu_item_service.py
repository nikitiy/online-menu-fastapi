from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.repositories import CompanyRepository
from src.backoffice.apps.menu.models import MenuItem
from src.backoffice.apps.menu.repositories import CategoryRepository, MenuItemRepository
from src.backoffice.apps.menu.schemas import MenuItemCreate, MenuItemUpdate
from src.backoffice.core.exceptions import NotFoundError
from src.backoffice.core.services import SlugService


class MenuItemService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = MenuItemRepository(session)
        self.category_repository = CategoryRepository(session)
        self.company_repository = CompanyRepository(session)

    async def create(self, menu_item_data: MenuItemCreate) -> MenuItem:
        menu_item_data_dict = menu_item_data.model_dump(
            exclude={"category_slug", "company_subdomain"}
        )
        menu_item_data_dict["slug"] = ""

        category = await self.category_repository.get_by_slug(
            menu_item_data.category_slug
        )
        if not category:
            raise NotFoundError(
                f"Category with slug '{menu_item_data.category_slug}' not found"
            )
        menu_item_data_dict["category_id"] = category.id

        company = await self.company_repository.get_by_subdomain(
            menu_item_data.company_subdomain
        )
        if not company:
            raise NotFoundError(
                f"Company with subdomain '{menu_item_data.company_subdomain}' not found"
            )
        menu_item_data_dict["owner_company_id"] = company.id

        menu_item = await self.repository.create(**menu_item_data_dict)

        SlugService.set_slug(instance=menu_item, name=menu_item.name)
        await self.session.flush()

        return menu_item

    async def get_by_slug(self, slug: str) -> Optional[MenuItem]:
        return await self.repository.get_by_slug(slug)

    async def get_by_slug_with_relations(self, slug: str) -> Optional[MenuItem]:
        """Get menu item by slug with all relations loaded"""
        return await self.repository.get_by_slug_with_relations(slug)

    async def get_by_id_with_relations(self, item_id: int) -> Optional[MenuItem]:
        """Get menu item by ID with all relations loaded"""
        return await self.repository.get_by_id_with_relations(item_id)

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
        update_dict = update_data.model_dump(
            exclude_unset=True, exclude={"category_slug", "company_subdomain"}
        )

        if update_data.category_slug is not None:
            category = await self.category_repository.get_by_slug(
                update_data.category_slug
            )
            if not category:
                raise NotFoundError(
                    f"Category with slug '{update_data.category_slug}' not found"
                )
            update_dict["category_id"] = category.id

        if update_data.company_subdomain is not None:
            company = await self.company_repository.get_by_subdomain(
                update_data.company_subdomain
            )
            if not company:
                raise NotFoundError(
                    f"Company with subdomain '{update_data.company_subdomain}' not found"
                )
            update_dict["owner_company_id"] = company.id

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
