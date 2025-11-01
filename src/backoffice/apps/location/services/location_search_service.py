from typing import Any, Dict, List, Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.location.models import (Address, City, Country,
                                                 Region, Street)
from src.backoffice.apps.location.services.address_service import \
    AddressService
from src.backoffice.apps.location.services.city_service import CityService
from src.backoffice.apps.location.services.country_service import \
    CountryService
from src.backoffice.apps.location.services.region_service import RegionService
from src.backoffice.apps.location.services.street_service import StreetService


class LocationSearchService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.country_service = CountryService(session)
        self.region_service = RegionService(session)
        self.city_service = CityService(session)
        self.street_service = StreetService(session)
        self.address_service = AddressService(session)

    async def _search_entities(
        self,
        query: str,
        search_fields: List[Any],
        base_conditions: List[Any] = None,
        limit: int = 10,
        model_class: Any = None,
    ) -> Sequence[Any]:
        conditions = list(base_conditions) if base_conditions else []

        if query and search_fields:
            search_condition = or_(
                *[field.ilike(f"%{query}%") for field in search_fields]
            )
            conditions.append(search_condition)

        stmt = select(model_class)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        entities = result.scalars().all()

        return entities

    async def search_locations(
        self,
        query: str,
        country_id: Optional[int] = None,
        region_id: Optional[int] = None,
        city_id: Optional[int] = None,
        limit: int = 10,
    ) -> Dict[str, List[Any]]:
        results = {
            "countries": [],
            "regions": [],
            "cities": [],
            "streets": [],
            "addresses": [],
        }

        if not country_id:
            countries = await self._search_entities(
                query=query,
                search_fields=[Country.name, Country.name_en],
                limit=limit,
                model_class=Country,
            )
            results["countries"] = list(countries)

        if not region_id:
            region_conditions = []
            if country_id:
                region_conditions.append(Region.country_id == country_id)

            regions = await self._search_entities(
                query=query,
                search_fields=[Region.name, Region.name_en],
                base_conditions=region_conditions,
                limit=limit,
                model_class=Region,
            )
            results["regions"] = list(regions)

        if not city_id:
            city_conditions = []
            if country_id:
                city_conditions.append(City.country_id == country_id)
            if region_id:
                city_conditions.append(City.region_id == region_id)

            cities = await self._search_entities(
                query=query,
                search_fields=[City.name, City.name_en],
                base_conditions=city_conditions,
                limit=limit,
                model_class=City,
            )
            results["cities"] = list(cities)

        # Search streets
        street_conditions = []
        if city_id:
            street_conditions.append(Street.city_id == city_id)

        streets = await self._search_entities(
            query=query,
            search_fields=[Street.name, Street.name_en],
            base_conditions=street_conditions,
            limit=limit,
            model_class=Street,
        )
        results["streets"] = list(streets)

        address_conditions = []
        if city_id:
            street_stmt = select(Street.id).where(Street.city_id == city_id)
            street_result = await self.session.execute(street_stmt)
            street_ids = [row[0] for row in street_result.fetchall()]
            if street_ids:
                address_conditions.append(Address.street_id.in_(street_ids))

        addresses = await self._search_entities(
            query=query,
            search_fields=[Address.house_number, Address.building, Address.apartment],
            base_conditions=address_conditions,
            limit=limit,
            model_class=Address,
        )
        results["addresses"] = list(addresses)

        return results

    async def search_locations_safe(
        self,
        query: str,
        country_id: Optional[int] = None,
        region_id: Optional[int] = None,
        city_id: Optional[int] = None,
        limit: int = 10,
    ) -> Dict[str, List[Any]]:
        if not query or len(query.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query must be at least 2 characters long",
            )

        if limit <= 0 or limit > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 50",
            )

        return await self.search_locations(
            query=query,
            country_id=country_id,
            region_id=region_id,
            city_id=city_id,
            limit=limit,
        )

    async def search_by_hierarchy(
        self,
        query: str,
        country_id: Optional[int] = None,
        region_id: Optional[int] = None,
        city_id: Optional[int] = None,
        limit: int = 10,
    ) -> Dict[str, List[Any]]:
        results = {
            "countries": [],
            "regions": [],
            "cities": [],
            "streets": [],
            "addresses": [],
        }

        region_conditions = []
        city_conditions = []
        street_conditions = []
        address_conditions = []

        if country_id:
            region_conditions.append(Region.country_id == country_id)
            city_conditions.append(City.country_id == country_id)

        if region_id:
            city_conditions.append(City.region_id == region_id)

        if city_id:
            street_conditions.append(Street.city_id == city_id)
            street_stmt = select(Street.id).where(Street.city_id == city_id)
            street_result = await self.session.execute(street_stmt)
            street_ids = [row[0] for row in street_result.fetchall()]
            if street_ids:
                address_conditions.append(Address.street_id.in_(street_ids))

        if not country_id:
            countries = await self._search_entities(
                query=query,
                search_fields=[Country.name, Country.name_en],
                limit=limit,
                model_class=Country,
            )
            results["countries"] = list(countries)

        if not region_id:
            regions = await self._search_entities(
                query=query,
                search_fields=[Region.name, Region.name_en],
                base_conditions=region_conditions,
                limit=limit,
                model_class=Region,
            )
            results["regions"] = list(regions)

        if not city_id:
            cities = await self._search_entities(
                query=query,
                search_fields=[City.name, City.name_en],
                base_conditions=city_conditions,
                limit=limit,
                model_class=City,
            )
            results["cities"] = list(cities)

        streets = await self._search_entities(
            query=query,
            search_fields=[Street.name, Street.name_en],
            base_conditions=street_conditions,
            limit=limit,
            model_class=Street,
        )
        results["streets"] = list(streets)

        addresses = await self._search_entities(
            query=query,
            search_fields=[Address.house_number, Address.building, Address.apartment],
            base_conditions=address_conditions,
            limit=limit,
            model_class=Address,
        )
        results["addresses"] = list(addresses)

        return results

    async def get_location_hierarchy(
        self,
        country_id: Optional[int] = None,
        region_id: Optional[int] = None,
        city_id: Optional[int] = None,
    ) -> Dict[str, List[Any]]:
        results = {
            "countries": [],
            "regions": [],
            "cities": [],
            "streets": [],
        }

        if country_id:
            country = await self.country_service.get_country(country_id)
            if country:
                results["countries"] = [country]
        else:
            countries = await self._search_entities(
                query="", search_fields=[Country.name], limit=100, model_class=Country
            )
            results["countries"] = list(countries)

        if region_id:
            region = await self.region_service.get_region(region_id)
            if region:
                results["regions"] = [region]
        elif country_id:
            regions = await self._search_entities(
                query="",
                search_fields=[Region.name],
                base_conditions=[Region.country_id == country_id],
                limit=100,
                model_class=Region,
            )
            results["regions"] = list(regions)

        if city_id:
            city = await self.city_service.get_city(city_id)
            if city:
                results["cities"] = [city]
        elif region_id:
            cities = await self._search_entities(
                query="",
                search_fields=[City.name],
                base_conditions=[City.region_id == region_id],
                limit=100,
                model_class=City,
            )
            results["cities"] = list(cities)
        elif country_id:
            cities = await self._search_entities(
                query="",
                search_fields=[City.name],
                base_conditions=[City.country_id == country_id],
                limit=100,
                model_class=City,
            )
            results["cities"] = list(cities)

        if city_id:
            streets = await self._search_entities(
                query="",
                search_fields=[Street.name],
                base_conditions=[Street.city_id == city_id],
                limit=100,
                model_class=Street,
            )
            results["streets"] = list(streets)

        return results
