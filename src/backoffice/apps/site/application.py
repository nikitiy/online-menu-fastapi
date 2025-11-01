from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.site.services import SiteService


class SiteApplication:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.site_service = SiteService(session)
