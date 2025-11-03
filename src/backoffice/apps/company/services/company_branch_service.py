from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.models import CompanyBranch
from src.backoffice.apps.company.repositories import (
    CompanyBranchRepository,
    CompanyRepository,
)
from src.backoffice.apps.company.schemas import CompanyBranchCreate, CompanyBranchUpdate


class CompanyBranchService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = CompanyBranchRepository(session)
        self.company_repository = CompanyRepository(session)

    async def create_branch(self, branch_data: CompanyBranchCreate) -> CompanyBranch:
        return await self.repository.create(**branch_data.model_dump())

    async def get_branch_by_id(self, branch_id: int) -> Optional[CompanyBranch]:
        return await self.repository.get_by_id(branch_id)

    async def get_branches_by_company(self, company_id: int) -> List[CompanyBranch]:
        return await self.repository.get_all(filters={"company_id": company_id})

    async def update_branch(
        self, branch_id: int, branch_data: CompanyBranchUpdate
    ) -> Optional[CompanyBranch]:
        update_data = branch_data.model_dump(exclude_unset=True)
        return await self.repository.update(branch_id, **update_data)

    async def delete_branch(self, branch_id: int) -> bool:
        return await self.repository.delete(branch_id)
