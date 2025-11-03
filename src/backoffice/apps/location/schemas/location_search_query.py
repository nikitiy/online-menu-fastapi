from typing import Optional

from pydantic import BaseModel, Field


class LocationSearchQuery(BaseModel):
    """Location search query parameters"""

    query: str = Field(..., description="Search query", min_length=1, max_length=1000)
    country_id: Optional[int] = Field(None, description="Country ID to limit search")
    region_id: Optional[int] = Field(None, description="Region ID to limit search")
    city_id: Optional[int] = Field(None, description="City ID to limit search")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of results")
