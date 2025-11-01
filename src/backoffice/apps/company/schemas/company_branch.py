from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CompanyBranchBase(BaseModel):
    """Basic company branch schema"""

    name: str = Field(..., min_length=1, max_length=255, description="Name")
    description: Optional[str] = Field(None, description="Description")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    address_id: Optional[int] = Field(None, description="Address ID")
    phone: Optional[str] = Field(None, max_length=50, description="Phone")
    email: Optional[EmailStr] = Field(None, description="Email")
    external_id: Optional[str] = Field(None, max_length=100, description="External ID")


class CompanyBranchCreate(CompanyBranchBase):
    """Create company branch schema"""

    company_id: int = Field(..., description="Company ID")


class CompanyBranchUpdate(BaseModel):
    """Update company branch schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Name")
    description: Optional[str] = Field(None, description="Description")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    address_id: Optional[int] = Field(None, description="Address ID")
    phone: Optional[str] = Field(None, max_length=50, description="Phone")
    email: Optional[EmailStr] = Field(None, description="Email")
    is_active: Optional[bool] = Field(None, description="Is active")
    is_verified: Optional[bool] = Field(None, description="Is verified")
    external_id: Optional[str] = Field(None, max_length=100, description="External ID")


class CompanyBranchInDB(CompanyBranchBase):
    """Company branch in the database schema"""

    id: int
    company_id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyBranch(CompanyBranchInDB):
    """Public company branch schema"""

    pass
