from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.models import CompanyBranch
from src.backoffice.apps.company.repositories import (
    CompanyBranchRepository,
    CompanyRepository,
)
from src.backoffice.apps.company.schemas import CompanyBranchCreate, CompanyBranchUpdate
from src.backoffice.core.exceptions import NotFoundError


class CompanyBranchService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = CompanyBranchRepository(session)
        self.company_repository = CompanyRepository(session)

    async def create_branch(self, branch_data: CompanyBranchCreate) -> CompanyBranch:
        return await self.repository.create(**branch_data.model_dump())

    async def get_branch_by_id_or_raise(self, branch_id: int) -> CompanyBranch:
        branch = await self.repository.get_by_id(branch_id)
        if not branch:
            raise NotFoundError(f"Company branch with id {branch_id} not found")
        return branch

    async def get_branches_by_company(self, company_id: int) -> List[CompanyBranch]:
        return await self.repository.get_all(filters={"company_id": company_id})

    async def update_branch_or_raise(
        self, branch_id: int, branch_data: CompanyBranchUpdate
    ) -> CompanyBranch:
        updated_branch = await self.repository.update(
            branch_id, **branch_data.model_dump(exclude_unset=True)
        )
        if not updated_branch:
            raise NotFoundError(f"Company branch with id {branch_id} not found")
        return updated_branch

    async def delete_branch_or_raise(self, branch_id: int) -> None:
        result = await self.repository.delete(branch_id)
        if not result:
            raise NotFoundError(f"Company branch with id {branch_id} not found")
