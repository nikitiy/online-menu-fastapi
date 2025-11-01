from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class StreetBase(BaseModel):
    """Base street schema"""

    name: str = Field(..., description="Name", max_length=255)
    name_en: str = Field(..., description="Eng name", max_length=255)
    city_id: int = Field(..., description="City ID")
    latitude: Optional[float] = Field(None, description="Latitude", ge=-90, le=90)
    longitude: Optional[float] = Field(None, description="Longitude", ge=-180, le=180)
    street_type: Optional[str] = Field(None, description="Street type", max_length=50)
    description: Optional[str] = Field(None, description="Description")
    is_active: bool = Field(True, description="Is active")


class StreetCreate(StreetBase):
    """Create street schema"""

    pass


class StreetUpdate(BaseModel):
    """Update street schema"""

    name: Optional[str] = Field(None, max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    city_id: Optional[int] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    street_type: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class StreetResponse(StreetBase):
    """Response street schema"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StreetListResponse(BaseModel):
    """List street schema"""

    streets: list[StreetResponse]
    total: int
    page: int
    size: int
    pages: int
