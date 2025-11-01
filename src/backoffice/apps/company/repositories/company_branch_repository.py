from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.models import CompanyBranch
from src.backoffice.core.repositories import BaseRepository


class CompanyBranchRepository(BaseRepository[CompanyBranch]):
    def __init__(self, session: AsyncSession):
        super().__init__(CompanyBranch, session)
