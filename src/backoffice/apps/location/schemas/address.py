from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AddressBase(BaseModel):
    """Base address schema"""

    house_number: Optional[str] = Field(None, description="House number", max_length=20)
    building: Optional[str] = Field(None, description="Building", max_length=20)
    apartment: Optional[str] = Field(None, description="Apartment", max_length=20)
    entrance: Optional[str] = Field(None, description="Entrance", max_length=20)
    floor: Optional[int] = Field(None, description="Floor", ge=0)
    street_id: int = Field(..., description="Street ID")
    latitude: Optional[float] = Field(None, description="Latitude", ge=-90, le=90)
    longitude: Optional[float] = Field(None, description="Longitude", ge=-180, le=180)
    postal_code: Optional[str] = Field(None, description="Postal code", max_length=20)
    description: Optional[str] = Field(None, description="Description")
    is_verified: bool = Field(False, description="Is verified")
    is_active: bool = Field(True, description="Is active")
    external_id: Optional[str] = Field(None, description="External ID", max_length=100)
    geocoder_provider: Optional[str] = Field(
        None, description="Geocoder provider", max_length=50
    )


class AddressCreate(AddressBase):
    """Create address schema"""

    pass


class AddressUpdate(BaseModel):
    """Update address schema"""

    house_number: Optional[str] = Field(None, max_length=20)
    building: Optional[str] = Field(None, max_length=20)
    apartment: Optional[str] = Field(None, max_length=20)
    entrance: Optional[str] = Field(None, max_length=20)
    floor: Optional[int] = Field(None, ge=0)
    street_id: Optional[int] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    postal_code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None
    external_id: Optional[str] = Field(None, max_length=100)
    geocoder_provider: Optional[str] = Field(None, max_length=50)


class AddressResponse(AddressBase):
    """Response address schema"""

    id: int
    full_address: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AddressListResponse(BaseModel):
    """List address schema"""

    addresses: list[AddressResponse]
    total: int
    page: int
    size: int
    pages: int
