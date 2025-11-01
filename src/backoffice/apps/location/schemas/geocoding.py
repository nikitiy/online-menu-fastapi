from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class GeocodingAccuracy(str, Enum):
    """Geocoding accuracy"""

    ROOFTOP = "ROOFTOP"
    RANGE_INTERPOLATED = "RANGE_INTERPOLATED"
    GEOMETRIC_CENTER = "GEOMETRIC_CENTER"
    APPROXIMATE = "APPROXIMATE"


class GeocodingProvider(str, Enum):
    """Geocoding provider"""

    GOOGLE = "google"
    YANDEX = "yandex"
    NOMINATIM = "nominatim"
    MAPBOX = "mapbox"


class GeocodingRequest(BaseModel):
    """Geocoding request schema"""

    query: str = Field(
        ..., description="Address for geocoding", min_length=1, max_length=1000
    )
    provider: Optional[GeocodingProvider] = Field(
        GeocodingProvider.GOOGLE, description="Provider for geocoding"
    )
    language: Optional[str] = Field("ru", description="Language", max_length=10)
    region: Optional[str] = Field(None, description="Region", max_length=100)
    bounds: Optional[str] = Field(
        None, description="Search boundaries (lat1,lng1,lat2,lng2)"
    )
    components: Optional[str] = Field(
        None, description="Address components for filtering"
    )


class GeocodingResultBase(BaseModel):
    """Base geocoding result schema"""

    query: str = Field(..., description="Original request")
    latitude: Optional[float] = Field(None, description="Latitude", ge=-90, le=90)
    longitude: Optional[float] = Field(None, description="Longitude", ge=-180, le=180)
    formatted_address: Optional[str] = Field(None, description="Formatted address")
    country: Optional[str] = Field(None, description="Country", max_length=255)
    region: Optional[str] = Field(None, description="Region", max_length=255)
    city: Optional[str] = Field(None, description="City", max_length=255)
    street: Optional[str] = Field(None, description="Street", max_length=255)
    house_number: Optional[str] = Field(None, description="House number", max_length=50)
    postal_code: Optional[str] = Field(None, description="Postal code", max_length=20)
    place_id: Optional[str] = Field(None, description="Place ID", max_length=255)
    place_type: Optional[str] = Field(None, description="Place type", max_length=100)
    accuracy: Optional[GeocodingAccuracy] = Field(None, description="Accuracy")
    confidence: Optional[float] = Field(None, description="Confidence", ge=0.0, le=1.0)
    provider: GeocodingProvider = Field(..., description="Provider")
    external_id: Optional[str] = Field(None, description="External ID", max_length=255)
    is_successful: bool = Field(True, description="Is successful")
    error_message: Optional[str] = Field(None, description="Error message")


class GeocodingResultCreate(GeocodingResultBase):
    """Create geocoding result schema"""

    raw_response: Optional[str] = Field(None, description="Raw response")
    expires_at: Optional[datetime] = Field(None, description="Cache expiration time")
    address_id: Optional[int] = Field(None, description="Address ID")


class GeocodingResultResponse(GeocodingResultBase):
    """Response geocoding result schema"""

    id: int
    created_at: datetime
    expires_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class GeocodingSearchRequest(BaseModel):
    """Geocoding search request schema"""

    query: str = Field(..., description="Search query", min_length=1, max_length=1000)
    provider: Optional[GeocodingProvider] = Field(
        GeocodingProvider.GOOGLE, description="Provider"
    )
    language: Optional[str] = Field("ru", description="Language", max_length=10)
    region: Optional[str] = Field(None, description="Region", max_length=100)
    bounds: Optional[str] = Field(None, description="Search boundaries")
    components: Optional[str] = Field(None, description="Address components")
    limit: Optional[int] = Field(
        10, description="Maximum number of results", ge=1, le=50
    )


class GeocodingSearchResponse(BaseModel):
    """Response geocoding search schema"""

    results: List[GeocodingResultResponse]
    total: int
    query: str
    provider: GeocodingProvider


class ReverseGeocodingRequest(BaseModel):
    """Reverse geocoding request schema"""

    latitude: float = Field(..., description="Latitude", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude", ge=-180, le=180)
    provider: Optional[GeocodingProvider] = Field(
        GeocodingProvider.GOOGLE, description="Provider"
    )
    language: Optional[str] = Field("ru", description="Language", max_length=10)
    result_type: Optional[str] = Field(None, description="Result types for filtering")


class GeocodingListResponse(BaseModel):
    """List geocoding response schema"""

    results: List[GeocodingResultResponse]
    total: int
    page: int
    size: int
    pages: int
