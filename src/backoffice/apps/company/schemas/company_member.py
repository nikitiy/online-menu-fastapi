from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.backoffice.apps.company.models.types import CompanyRole


class CompanyMemberCreate(BaseModel):
    """Create company member schema"""

    user_id: int = Field(..., description="User ID")
    role: CompanyRole = Field(..., description="Role")


class CompanyMemberCreateByEmail(BaseModel):
    """Create company member by email schema"""

    user_email: str = Field(..., description="User email")


class CompanyMemberUpdate(BaseModel):
    """Update company member schema"""

    role: CompanyRole = Field(..., description="Role")


class CompanyMemberUpdateByEmail(BaseModel):
    """Update company member role by email schema"""

    user_email: str = Field(..., description="User email")
    role: CompanyRole = Field(..., description="New role")


class CompanyMemberInDB(BaseModel):
    """Company member in the database schema"""

    id: int
    company_id: int
    user_id: int
    role: CompanyRole
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyMemberResponse(CompanyMemberInDB):
    """Company member response schema"""

    pass


class CompanyMemberCreateByEmailResponse(BaseModel):
    """Response schema for creating company member by email"""

    message: str = Field(..., description="Success message")
    company_member: CompanyMemberResponse = Field(
        ..., description="Created company member"
    )
