from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.location.models import GeocodingResult
from src.backoffice.core.repositories import BaseRepository


class GeocodingResultRepository(BaseRepository[GeocodingResult]):
    def __init__(self, session: AsyncSession):
        super().__init__(GeocodingResult, session)
