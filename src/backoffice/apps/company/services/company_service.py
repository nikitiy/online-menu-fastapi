from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.exceptions import SubdomainAlreadyTaken
from src.backoffice.apps.company.models import Company
from src.backoffice.apps.company.repositories import CompanyRepository
from src.backoffice.apps.company.schemas import CompanyCreate


class CompanyService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = CompanyRepository(session)

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

        return company

    async def get_accessible_companies_for_user(self, user_id: int) -> List[Company]:
        return await self.repository.select_user_companies(user_id)
