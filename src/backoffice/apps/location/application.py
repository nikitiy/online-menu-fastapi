from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.location.schemas import (AddressCreate,
                                                  AddressResponse, CityCreate,
                                                  CityResponse, CountryCreate,
                                                  CountryResponse,
                                                  CountryUpdate, RegionCreate,
                                                  RegionResponse, StreetCreate,
                                                  StreetResponse)
from src.backoffice.apps.location.schemas.geocoding import (
    GeocodingRequest, GeocodingResultResponse, GeocodingSearchRequest,
    GeocodingSearchResponse, ReverseGeocodingRequest)
from src.backoffice.apps.location.services.geocoder_service import \
    GeocoderService
from src.backoffice.apps.location.services.location_service import \
    LocationService


class LocationApplication:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.location_service = LocationService(session)
        self.geocoder_service = GeocoderService(session)

    # ==================== COUNTRY METHODS ====================

    async def create_country(self, country_data: CountryCreate) -> CountryResponse:
        country = await self.location_service.create_country(country_data)
        await self.session.commit()
        return country

    async def get_country(self, country_id: int) -> CountryResponse:
        return await self.location_service.get_country(country_id)

    async def get_countries(self) -> List[CountryResponse]:
        countries = await self.location_service.get_countries()
        return countries

    async def update_country(
        self, country_id: int, country_data: CountryUpdate
    ) -> CountryResponse:
        country = await self.location_service.update_country(country_id, country_data)
        await self.session.commit()
        return country

    async def delete_country(self, country_id: int):
        await self.location_service.delete_country(country_id)
        await self.session.commit()

    # ==================== REGION METHODS ====================

    async def create_region(self, region_data: RegionCreate) -> RegionResponse:
        region = await self.location_service.create_region(region_data)
        await self.session.commit()
        return region

    async def get_region(self, region_id: int) -> RegionResponse:
        return await self.location_service.get_region(region_id)

    async def get_regions_by_country(
        self,
        country_id: int,
    ) -> List[RegionResponse]:
        regions = await self.location_service.get_regions_by_country(country_id)
        return regions

    # ==================== CITY METHODS ====================

    async def create_city(self, city_data: CityCreate) -> CityResponse:
        city = await self.location_service.create_city(city_data)
        await self.session.commit()
        return city

    async def get_city(self, city_id: int) -> CityResponse:
        return await self.location_service.get_city(city_id)

    async def get_cities_by_country(
        self,
        country_id: int,
    ) -> List[CityResponse]:
        cities = await self.location_service.get_cities_by_country(country_id)
        return cities

    async def get_cities_by_region(
        self,
        region_id: int,
    ) -> List[CityResponse]:
        cities = await self.location_service.get_cities_by_region(region_id)
        return cities

    # ==================== STREET METHODS ====================

    async def create_street(self, street_data: StreetCreate) -> StreetResponse:
        street = await self.location_service.create_street(street_data)
        await self.session.commit()
        return street

    async def get_street(self, street_id: int) -> StreetResponse:
        return await self.location_service.get_street(street_id)

    async def get_streets_by_city(
        self,
        city_id: int,
    ) -> List[StreetResponse]:
        streets = await self.location_service.get_streets_by_city(city_id)
        return streets

    # ==================== ADDRESS METHODS ====================

    async def create_address(self, address_data: AddressCreate) -> AddressResponse:
        address = await self.location_service.create_address(address_data)
        await self.session.commit()
        return address

    async def get_address(self, address_id: int) -> AddressResponse:
        return await self.location_service.get_address(address_id)

    async def get_addresses_by_street(
        self,
        street_id: int,
    ) -> List[AddressResponse]:
        addresses = await self.location_service.get_addresses_by_street(street_id)
        return addresses

    # ==================== SEARCH METHODS ====================

    async def search_locations(
        self,
        query: str,
        country_id: Optional[int] = None,
        region_id: Optional[int] = None,
        city_id: Optional[int] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        return await self.location_service.search_locations(
            query, country_id, region_id, city_id, limit
        )

    # ==================== GEOCODING METHODS ====================

    async def geocode_address(
        self, request: GeocodingRequest
    ) -> List[GeocodingResultResponse]:
        return await self.geocoder_service.geocode_safe(request)

    async def search_addresses(
        self, request: GeocodingSearchRequest
    ) -> GeocodingSearchResponse:
        return await self.geocoder_service.search_safe(request)

    async def reverse_geocode(
        self, request: ReverseGeocodingRequest
    ) -> List[GeocodingResultResponse]:
        return await self.geocoder_service.reverse_geocode_safe(request)

    async def get_available_providers(self) -> List[str]:
        return await self.geocoder_service.get_available_providers()

    async def get_provider_status(self, provider: str) -> Dict[str, Any]:
        return await self.geocoder_service.get_provider_status(provider)

    async def get_health_status(self) -> Dict[str, Any]:
        return await self.geocoder_service.get_health_status()
