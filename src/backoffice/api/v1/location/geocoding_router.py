from typing import List

from fastapi import APIRouter

from src.backoffice.apps.location.schemas.geocoding import (
    GeocodingRequest,
    GeocodingResultResponse,
    GeocodingSearchRequest,
    GeocodingSearchResponse,
    ReverseGeocodingRequest,
)
from src.backoffice.core.dependencies import LocationApplicationDep

router = APIRouter(prefix="/geocoding", tags=["geocoding"])


@router.post("/geocode", response_model=List[GeocodingResultResponse])
async def geocode_address(
    request: GeocodingRequest,
    location_app: LocationApplicationDep,
):
    """
    Address Geocoding

    Converts a text address into geographic coordinates (latitude, longitude)
    Supports multiple providers: Google Maps, Yandex Maps, OpenStreetMap Nominatim
    """
    return await location_app.geocode_address(request)


@router.post("/search", response_model=GeocodingSearchResponse)
async def search_addresses(
    request: GeocodingSearchRequest,
    location_app: LocationApplicationDep,
):
    """
    Address Search

    Performs address searches based on your query, with the option to limit the number of results
    """
    return await location_app.search_addresses(request)


@router.post("/reverse", response_model=List[GeocodingResultResponse])
async def reverse_geocode(
    request: ReverseGeocodingRequest,
    location_app: LocationApplicationDep,
):
    """
    Reverse Geocoding

    Converts geographic coordinates into a text address
    """
    return await location_app.reverse_geocode(request)


@router.get("/providers", response_model=List[str])
async def get_available_providers(location_app: LocationApplicationDep):
    """
    Getting a list of available geocoding providers

    Returns a list of providers that are configured and available for use
    """
    return await location_app.get_available_providers()


@router.get("/providers/{provider}/status")
async def get_provider_status(provider: str, location_app: LocationApplicationDep):
    """
    Getting provider status

    Returns information about the availability and configuration of a specific provider
    """
    return await location_app.get_provider_status(provider)


@router.get("/health")
async def health_check(location_app: LocationApplicationDep):
    """
    Geocoding service health check

    Returns the availability status of the service and its components
    """
    return await location_app.get_health_status()
