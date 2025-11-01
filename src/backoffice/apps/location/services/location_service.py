import logging
import re
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.location.repositories import GeocodingResultRepository
from src.backoffice.apps.location.schemas import (AddressCreate, CityCreate,
                                                  CountryCreate, CountryUpdate,
                                                  RegionCreate, StreetCreate)
from src.backoffice.apps.location.services.address_service import \
    AddressService
from src.backoffice.apps.location.services.city_service import CityService
from src.backoffice.apps.location.services.country_service import \
    CountryService
from src.backoffice.apps.location.services.geocoder_service import \
    GeocoderService
from src.backoffice.apps.location.services.location_search_service import \
    LocationSearchService
from src.backoffice.apps.location.services.region_service import RegionService
from src.backoffice.apps.location.services.street_service import StreetService

logger = logging.getLogger(__name__)


class LocationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.geocoder_service = GeocoderService(session)

        self.country_service = CountryService(session)
        self.region_service = RegionService(session)
        self.city_service = CityService(session)
        self.street_service = StreetService(session)
        self.address_service = AddressService(session)
        self.search_service = LocationSearchService(session)
        self.geocoding_result_repository = GeocodingResultRepository(session)

    # ==================== COUNTRY METHODS ====================

    async def create_country(self, country_data: CountryCreate):
        return await self.country_service.create_country(country_data)

    async def get_country(self, country_id: int):
        return await self.country_service.get_country(country_id)

    async def get_countries(self):
        return await self.country_service.get_countries()

    async def update_country(self, country_id: int, country_data: CountryUpdate):
        return await self.country_service.update_country(country_id, country_data)

    async def delete_country(self, country_id: int) -> bool:
        return await self.country_service.delete_country(country_id)

    # ==================== REGION METHODS ====================

    async def create_region(self, region_data: RegionCreate):
        return await self.region_service.create_region(region_data)

    async def get_region(self, region_id: int):
        return await self.region_service.get_region(region_id)

    async def get_regions_by_country(self, country_id: int):
        return await self.region_service.get_regions_by_country(country_id)

    async def update_region(self, region_id: int, region_data: dict):
        return await self.region_service.update_region(region_id, region_data)

    async def delete_region(self, region_id: int) -> bool:
        return await self.region_service.delete_region(region_id)

    # ==================== CITY METHODS ====================

    async def create_city(self, city_data: CityCreate):
        return await self.city_service.create_city(city_data)

    async def get_city(self, city_id: int):
        return await self.city_service.get_city(city_id)

    async def get_cities_by_country(self, country_id: int):
        return await self.city_service.get_cities_by_country(country_id)

    async def get_cities_by_region(self, region_id: int):
        return await self.city_service.get_cities_by_region(region_id)

    async def update_city(self, city_id: int, city_data: dict):
        return await self.city_service.update_city(city_id, city_data)

    async def delete_city(self, city_id: int) -> bool:
        return await self.city_service.delete_city(city_id)

    # ==================== STREET METHODS ====================

    async def create_street(self, street_data: StreetCreate):
        return await self.street_service.create_street(street_data)

    async def get_street(self, street_id: int):
        return await self.street_service.get_street(street_id)

    async def get_streets_by_city(self, city_id: int):
        return await self.street_service.get_streets_by_city(city_id)

    async def update_street(self, street_id: int, street_data: dict):
        return await self.street_service.update_street(street_id, street_data)

    async def delete_street(self, street_id: int) -> bool:
        return await self.street_service.delete_street(street_id)

    # ==================== ADDRESS METHODS ====================

    async def create_address(self, address_data: AddressCreate):
        return await self.address_service.create_address(address_data)

    async def get_address(self, address_id: int):
        return await self.address_service.get_address(address_id)

    async def get_addresses_by_street(self, street_id: int):
        return await self.address_service.get_addresses_by_street(street_id)

    async def update_address(self, address_id: int, address_data: dict):
        return await self.address_service.update_address(address_id, address_data)

    async def delete_address(self, address_id: int) -> bool:
        return await self.address_service.delete_address(address_id)

    # ==================== SEARCH METHODS ====================

    async def search_locations(
        self,
        query: str,
        country_id: Optional[int] = None,
        region_id: Optional[int] = None,
        city_id: Optional[int] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        return await self.search_service.search_locations(
            query, country_id, region_id, city_id, limit
        )

    async def search_locations_safe(
        self,
        query: str,
        country_id: Optional[int] = None,
        region_id: Optional[int] = None,
        city_id: Optional[int] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        return await self.search_service.search_locations_safe(
            query, country_id, region_id, city_id, limit
        )

    async def search_by_hierarchy(
        self,
        query: str,
        country_id: Optional[int] = None,
        region_id: Optional[int] = None,
        city_id: Optional[int] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        return await self.search_service.search_by_hierarchy(
            query, country_id, region_id, city_id, limit
        )

    async def get_location_hierarchy(
        self,
        country_id: Optional[int] = None,
        region_id: Optional[int] = None,
        city_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        return await self.search_service.get_location_hierarchy(
            country_id, region_id, city_id
        )

    # ==================== GEOCODING INTEGRATION ====================

    async def _find_or_create_country(self, country_name: str) -> int:
        if not country_name:
            raise ValueError("Country name is required")

        existing_country = await self.country_service.repository.get_by_name(
            country_name
        )

        if existing_country:
            return existing_country.id

        country_data = CountryCreate(
            name=country_name,
            name_en=country_name,
            code="UNK",
            code_alpha2="UN",
            phone_code=None,
            currency_code=None,
            timezone=None,
            description=f"Country created from geocoding: {country_name}",
            is_active=True,
        )

        country_response = await self.create_country(country_data)
        return country_response.id

    async def _find_or_create_region(
        self, region_name: str, country_id: int
    ) -> Optional[int]:
        if not region_name:
            return None

        existing_region = await self.region_service.repository.get_by_name(
            region_name, country_id
        )

        if existing_region:
            return existing_region.id

        region_data = RegionCreate(
            name=region_name,
            name_en=region_name,
            code=None,
            country_id=country_id,
            description=f"Region created from geocoding: {region_name}",
            is_active=True,
        )

        region_response = await self.create_region(region_data)
        return region_response.id

    async def _find_or_create_city(
        self,
        city_name: str,
        country_id: int,
        region_id: Optional[int] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> int:
        if not city_name:
            raise ValueError("City name is required")

        existing_city = await self.city_service.repository.get_by_name(
            city_name, country_id, region_id
        )

        if existing_city:
            return existing_city.id

        city_data = CityCreate(
            name=city_name,
            name_en=city_name,
            country_id=country_id,
            region_id=region_id,
            latitude=latitude,
            longitude=longitude,
            population=None,
            timezone=None,
            description=f"City created from geocoding: {city_name}",
            is_active=True,
        )

        city_response = await self.create_city(city_data)
        return city_response.id

    async def _find_or_create_street(self, street_name: str, city_id: int) -> int:
        if not street_name:
            raise ValueError("Street name is required")

        existing_street = await self.street_service.repository.get_by_name(
            street_name, city_id
        )

        if existing_street:
            return existing_street.id

        street_data = StreetCreate(
            name=street_name,
            name_en=street_name,
            city_id=city_id,
            latitude=None,
            longitude=None,
            street_type=None,
            description=f"Street created from geocoding: {street_name}",
            is_active=True,
        )

        street_response = await self.create_street(street_data)
        return street_response.id

    @staticmethod
    def _parse_address_components(
        formatted_address: str,
    ) -> tuple[Optional[str], Optional[str], Optional[str], Optional[int]]:
        if not formatted_address:
            return None, None, None, None

        building = None
        apartment = None
        entrance = None
        floor = None

        building_match = re.search(
            r"(?:корпус|корп\.?)\s*(\d+)", formatted_address, re.IGNORECASE
        )
        if building_match:
            building = building_match.group(1)

        apartment_match = re.search(
            r"(?:квартира|кв\.?)\s*(\d+)", formatted_address, re.IGNORECASE
        )
        if apartment_match:
            apartment = apartment_match.group(1)

        entrance_match = re.search(
            r"(?:подъезд|п\.?)\s*(\d+)", formatted_address, re.IGNORECASE
        )
        if entrance_match:
            entrance = entrance_match.group(1)

        floor_match = re.search(
            r"(?:этаж|эт\.?)\s*(\d+)", formatted_address, re.IGNORECASE
        )
        if floor_match:
            try:
                floor = int(floor_match.group(1))
            except ValueError:
                pass

        return building, apartment, entrance, floor

    async def create_address_from_geocoding(self, geocoding_result_id: int):
        geocoding_result = await self.geocoding_result_repository.get_by_id(
            geocoding_result_id
        )

        if not geocoding_result or not geocoding_result.is_successful:
            return None

        try:
            country_id = await self._find_or_create_country(
                str(geocoding_result.country)
            )
            region_id = await self._find_or_create_region(
                str(geocoding_result.region), country_id
            )
            city_id = await self._find_or_create_city(
                str(geocoding_result.city),
                country_id,
                region_id,
                geocoding_result.latitude,  # type: ignore
                geocoding_result.longitude,  # type: ignore
            )
            street_id = await self._find_or_create_street(
                str(geocoding_result.street), city_id
            )

            building, apartment, entrance, floor = self._parse_address_components(
                str(geocoding_result.formatted_address)
            )

            address_data = AddressCreate(
                house_number=str(geocoding_result.house_number),
                building=building,
                apartment=apartment,
                entrance=entrance,
                floor=floor,
                street_id=street_id,
                latitude=geocoding_result.latitude,  # type: ignore
                longitude=geocoding_result.longitude,  # type: ignore
                postal_code=str(geocoding_result.postal_code),
                description=str(geocoding_result.formatted_address),
                is_verified=True,
                is_active=True,
                external_id=str(geocoding_result.external_id),
                geocoder_provider=str(geocoding_result.provider),
            )

            address = await self.create_address(address_data)

            geocoding_result.address_id = address.id
            await self.session.commit()

            return address

        except Exception as e:
            logger.error(
                f"Error creating address from geocoding result {geocoding_result_id}: {e}"
            )
            await self.session.rollback()
            return None
