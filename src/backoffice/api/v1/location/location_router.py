from typing import List, Optional

from fastapi import APIRouter, Query

from src.backoffice.apps.location.schemas import (AddressCreate,
                                                  AddressResponse, CityCreate,
                                                  CityResponse, CountryCreate,
                                                  CountryResponse,
                                                  CountryUpdate, RegionCreate,
                                                  RegionResponse, StreetCreate,
                                                  StreetResponse)
from src.backoffice.core.dependencies.service_dependencies import \
    LocationApplicationDep

router = APIRouter(prefix="/locations", tags=["locations"])


# ==================== COUNTRIES ====================


@router.post("/countries", response_model=CountryResponse, status_code=201)
async def create_country(
    country_data: CountryCreate,
    location_app: LocationApplicationDep,
):
    """Create country"""
    return await location_app.create_country(country_data)


@router.get("/countries/{country_id}", response_model=CountryResponse)
async def get_country(
    country_id: int,
    location_app: LocationApplicationDep,
):
    """Get country by ID"""
    return await location_app.get_country(country_id)


@router.get("/countries", response_model=List[CountryResponse])
async def get_countries(
    location_app: LocationApplicationDep,
):
    """Get countries"""
    return await location_app.get_countries()


@router.put("/countries/{country_id}", response_model=CountryResponse)
async def update_country(
    country_id: int,
    country_data: CountryUpdate,
    location_app: LocationApplicationDep,
):
    """Update country"""
    return await location_app.update_country(country_id, country_data)


@router.delete("/countries/{country_id}", status_code=204)
async def delete_country(
    country_id: int,
    location_app: LocationApplicationDep,
):
    """Delete country"""
    await location_app.delete_country(country_id)


# ==================== REGIONS ====================


@router.post("/regions", response_model=RegionResponse, status_code=201)
async def create_region(
    region_data: RegionCreate,
    location_app: LocationApplicationDep,
):
    """Create region"""
    return await location_app.create_region(region_data)


@router.get("/regions/{region_id}", response_model=RegionResponse)
async def get_region(
    region_id: int,
    location_app: LocationApplicationDep,
):
    """Get region by ID"""
    return await location_app.get_region(region_id)


@router.get("/countries/{country_id}/regions", response_model=List[RegionResponse])
async def get_regions_by_country(
    country_id: int,
    location_app: LocationApplicationDep,
):
    """Get regions by country"""
    return await location_app.get_regions_by_country(country_id)


# ==================== CITIES ====================


@router.post("/cities", response_model=CityResponse, status_code=201)
async def create_city(
    city_data: CityCreate,
    location_app: LocationApplicationDep,
):
    """Create city"""
    return await location_app.create_city(city_data)


@router.get("/cities/{city_id}", response_model=CityResponse)
async def get_city(
    city_id: int,
    location_app: LocationApplicationDep,
):
    """Get city by ID"""
    return await location_app.get_city(city_id)


@router.get("/countries/{country_id}/cities", response_model=List[CityResponse])
async def get_cities_by_country(
    country_id: int,
    location_app: LocationApplicationDep,
):
    """Get cities by country"""
    return await location_app.get_cities_by_country(country_id)


@router.get("/regions/{region_id}/cities", response_model=List[CityResponse])
async def get_cities_by_region(
    region_id: int,
    location_app: LocationApplicationDep,
):
    """Get cities by region"""
    return await location_app.get_cities_by_region(region_id)


# ==================== STREETS ====================


@router.post("/streets", response_model=StreetResponse, status_code=201)
async def create_street(
    street_data: StreetCreate,
    location_app: LocationApplicationDep,
):
    """Create street"""
    return await location_app.create_street(street_data)


@router.get("/streets/{street_id}", response_model=StreetResponse)
async def get_street(
    street_id: int,
    location_app: LocationApplicationDep,
):
    """Get street by ID"""
    return await location_app.get_street(street_id)


@router.get("/cities/{city_id}/streets", response_model=List[StreetResponse])
async def get_streets_by_city(
    city_id: int,
    location_app: LocationApplicationDep,
):
    """Get streets by city"""
    return await location_app.get_streets_by_city(city_id)


# ==================== ADDRESSES ====================


@router.post("/addresses", response_model=AddressResponse, status_code=201)
async def create_address(
    address_data: AddressCreate,
    location_app: LocationApplicationDep,
):
    """Create address"""
    return await location_app.create_address(address_data)


@router.get("/addresses/{address_id}", response_model=AddressResponse)
async def get_address(
    address_id: int,
    location_app: LocationApplicationDep,
):
    """Get address by ID"""
    return await location_app.get_address(address_id)


@router.get("/streets/{street_id}/addresses", response_model=List[AddressResponse])
async def get_addresses_by_street(
    street_id: int,
    location_app: LocationApplicationDep,
):
    """Get addresses by street"""
    return await location_app.get_addresses_by_street(street_id)


# ==================== SEARCH ====================


@router.get("/search")
async def search_locations(
    location_app: LocationApplicationDep,
    query: str = Query(..., description="Search query"),
    country_id: Optional[int] = Query(None, description="Country ID to limit search"),
    region_id: Optional[int] = Query(None, description="Region ID to limit search"),
    city_id: Optional[int] = Query(None, description="City ID to limit search"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
):
    """
    Search locations by request

    Search by country, region, city, street, and address
    """
    return await location_app.search_locations(
        query=query,
        country_id=country_id,
        region_id=region_id,
        city_id=city_id,
        limit=limit,
    )
