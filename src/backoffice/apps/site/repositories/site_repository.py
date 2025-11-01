from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.site.models import Site
from src.backoffice.core.repositories import BaseRepository


class SiteRepository(BaseRepository[Site]):
    def __init__(self, session: AsyncSession):
        super().__init__(Site, session)

    async def get_by_company_id(self, company_id: int) -> Site | None:
        stmt = select(Site).where(Site.company_id == company_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
