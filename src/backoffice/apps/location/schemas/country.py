from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CountryBase(BaseModel):
    """Base country schema"""

    name: str = Field(..., description="Name", max_length=255)
    name_en: str = Field(..., description="Eng name", max_length=255)
    code: str = Field(..., description="ISO 3166-1 alpha-3 code", max_length=3)
    code_alpha2: str = Field(..., description="ISO 3166-1 alpha-2 code", max_length=2)
    phone_code: Optional[str] = Field(None, description="Phone code", max_length=10)
    currency_code: Optional[str] = Field(
        None, description="Currency code", max_length=3
    )
    timezone: Optional[str] = Field(None, description="Timezone", max_length=50)
    description: Optional[str] = Field(None, description="Description")
    is_active: bool = Field(True, description="Is active")


class CountryCreate(CountryBase):
    """Create country schema"""

    pass


class CountryUpdate(BaseModel):
    """Update country schema"""

    name: Optional[str] = Field(None, max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    code: Optional[str] = Field(None, max_length=3)
    code_alpha2: Optional[str] = Field(None, max_length=2)
    phone_code: Optional[str] = Field(None, max_length=10)
    currency_code: Optional[str] = Field(None, max_length=3)
    timezone: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CountryResponse(CountryBase):
    """Country response schema"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CountryListResponse(BaseModel):
    """List country schema"""

    countries: list[CountryResponse]
    total: int
    page: int
    size: int
    pages: int
