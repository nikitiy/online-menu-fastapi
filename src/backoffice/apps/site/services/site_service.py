from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.site.models import Site
from src.backoffice.apps.site.repositories import SiteRepository


class SiteService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = SiteRepository(session)

    async def create_site(self, company_id: int) -> Site:
        return await self.repository.create(company_id=company_id)

    async def get_site_by_company_id(self, company_id: int) -> Site | None:
        return await self.repository.get_by_company_id(company_id)

    async def get_site(self, site_id: int) -> Site | None:
        return await self.repository.get_by_id(site_id)
