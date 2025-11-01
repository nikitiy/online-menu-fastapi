from typing import Annotated, AsyncGenerator, TypeAlias

from fastapi import Depends
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from src.backoffice.core.config import db_settings

engine = create_async_engine(db_settings.ASYNC_DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


SessionDep: TypeAlias = Annotated[AsyncSession, Depends(get_session)]
