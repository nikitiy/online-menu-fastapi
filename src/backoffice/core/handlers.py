from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.backoffice.core.exceptions import NotFoundError, SubdomainAlreadyTaken


async def subdomain_already_taken_handler(
    _request: Request, exc: SubdomainAlreadyTaken
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
    )


async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )
