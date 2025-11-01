from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.backoffice.apps.company.models.types import CompanyRole


class CompanyMemberBase(BaseModel):
    """Base company member schema"""

    role: CompanyRole = Field(..., description="Role")


class CompanyMemberCreate(CompanyMemberBase):
    """Create company member schema"""

    user_id: int = Field(..., description="User ID")


class CompanyMemberCreateWithCompany(CompanyMemberBase):
    """Create company member with company ID schema"""

    user_id: int = Field(..., description="User ID")
    company_id: int = Field(..., description="Company ID")


class CompanyMemberUpdate(BaseModel):
    """Update company member schema"""

    role: CompanyRole = Field(..., description="Role")


class CompanyMemberUpdateRole(BaseModel):
    """Update company member role schema"""

    company_id: int = Field(..., description="Company ID")
    user_id: int = Field(..., description="User ID")
    role: CompanyRole = Field(..., description="New role")


class CompanyMemberRole(BaseModel):
    """Update company member role data schema"""

    role: CompanyRole = Field(..., description="New role")


class CompanyMemberInDB(CompanyMemberBase):
    """Company member in the database schema"""

    id: int
    company_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyMemberOut(CompanyMemberInDB):
    """Public company member schema"""

    pass


# Alias for backward compatibility
CompanyMember = CompanyMemberOut
