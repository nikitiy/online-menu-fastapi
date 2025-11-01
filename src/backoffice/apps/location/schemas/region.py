from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RegionBase(BaseModel):
    """Base region schema"""

    name: str = Field(..., description="Name", max_length=255)
    name_en: str = Field(..., description="Eng name", max_length=255)
    code: Optional[str] = Field(None, description="Code", max_length=20)
    country_id: int = Field(..., description="Country ID")
    description: Optional[str] = Field(None, description="Description")
    is_active: bool = Field(True, description="Is active")


class RegionCreate(RegionBase):
    """Create region schema"""

    pass


class RegionUpdate(BaseModel):
    """Схема для обновления региона"""

    name: Optional[str] = Field(None, max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    code: Optional[str] = Field(None, max_length=20)
    country_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RegionResponse(RegionBase):
    """Response region schema"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RegionListResponse(BaseModel):
    """List region schema"""

    regions: list[RegionResponse]
    total: int
    page: int
    size: int
    pages: int
