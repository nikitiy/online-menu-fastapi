from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.models import Company
from src.backoffice.apps.company.repositories import CompanyRepository
from src.backoffice.apps.company.schemas import CompanyCreate
from src.backoffice.apps.site.services import SiteService
from src.backoffice.core.exceptions import NotFoundError, SubdomainAlreadyTaken


class CompanyService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = CompanyRepository(session)
        self.site_service = SiteService(session)

    async def create_company(self, company_data: CompanyCreate) -> Company:
        if await self.repository.subdomain_exists(company_data.subdomain):
            raise SubdomainAlreadyTaken(
                f"Subdomain '{company_data.subdomain}' is already taken"
            )

        company = await self.repository.create(
            name=company_data.name,
            description=company_data.description,
            subdomain=company_data.subdomain,
            type_of_establishment=company_data.type_of_establishment,
            cuisine_category=company_data.cuisine_category,
        )

        await self.site_service.create_site(company.id)

        return company

    async def get_accessible_companies_for_user(self, user_id: int) -> List[Company]:
        return await self.repository.select_user_companies(user_id)

    async def get_by_subdomain_or_raise(self, subdomain: str) -> Company:
        company = await self.repository.get_by_subdomain(subdomain)
        if not company:
            raise NotFoundError(f"Company with subdomain '{subdomain}' not found")
        return company
