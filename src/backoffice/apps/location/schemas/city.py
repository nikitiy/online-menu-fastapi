from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CityBase(BaseModel):
    """Base city schema"""

    name: str = Field(..., description="Name", max_length=255)
    name_en: str = Field(..., description="Eng name", max_length=255)
    country_id: int = Field(..., description="Country ID")
    region_id: Optional[int] = Field(None, description="Region ID")
    latitude: Optional[float] = Field(None, description="Latitude", ge=-90, le=90)
    longitude: Optional[float] = Field(None, description="Longitude", ge=-180, le=180)
    population: Optional[int] = Field(None, description="Population", ge=0)
    timezone: Optional[str] = Field(None, description="Timezone", max_length=50)
    description: Optional[str] = Field(None, description="Description")
    is_active: bool = Field(True, description="Is active")


class CityCreate(CityBase):
    """Create city schema"""

    pass


class CityUpdate(BaseModel):
    """Update city schema"""

    name: Optional[str] = Field(None, max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    country_id: Optional[int] = None
    region_id: Optional[int] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    population: Optional[int] = Field(None, ge=0)
    timezone: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CityResponse(CityBase):
    """Response city schema"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CityListResponse(BaseModel):
    """List city schema"""

    cities: list[CityResponse]
    total: int
    page: int
    size: int
    pages: int
