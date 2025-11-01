from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.backoffice.apps.company.models.types import (
    CompanyEstablishmentType,
    CuisineCategory,
)


class CompanyBase(BaseModel):
    """Basic company schema"""

    name: str = Field(..., min_length=1, max_length=128, description="Company name")
    description: Optional[str] = Field(
        None, max_length=1000, description="Company description"
    )
    subdomain: str = Field(
        ...,
        min_length=1,
        max_length=63,
        pattern=r"^[a-z0-9-]+$",
        description="Company subdomain",
    )
    type_of_establishment: CompanyEstablishmentType = Field(
        default=CompanyEstablishmentType.RESTAURANT,
        description="Type of establishment",
    )
    cuisine_category: CuisineCategory = Field(
        default=CuisineCategory.OTHER,
        description="Cuisine category",
    )

    @field_validator("subdomain")
    @classmethod
    def validate_subdomain(cls, v):
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("Subdomain cannot start or end with hyphen")
        if "--" in v:
            raise ValueError("Subdomain cannot contain consecutive hyphens")
        return v


class CompanyCreate(CompanyBase):
    """Create company schema"""

    pass


class CompanyUpdate(CompanyBase):
    """Update company schema"""

    name: Optional[str] = None  # type: ignore[override]
    description: Optional[str] = None  # type: ignore[override]
    subdomain: Optional[str] = None  # type: ignore[override]
    type_of_establishment: Optional[CompanyEstablishmentType] = None  # type: ignore[override]
    cuisine_category: Optional[CuisineCategory] = None  # type: ignore[override]


class CompanyInDB(CompanyBase):
    """Company in the database schema"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyOut(CompanyInDB):
    """Public company schema"""


class CompanyShortOut(BaseModel):
    """Public short company schema"""

    name: str
    description: Optional[str]
    subdomain: str

    model_config = ConfigDict(from_attributes=True)
