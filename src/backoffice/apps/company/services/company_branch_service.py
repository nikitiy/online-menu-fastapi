from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.repositories import (CompanyBranchRepository,
                                                      CompanyRepository)


class CompanyBranchService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = CompanyBranchRepository(session)
        self.company_repository = CompanyRepository(session)
