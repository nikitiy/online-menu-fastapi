from fastapi import Request, status
from fastapi.responses import JSONResponse


async def subdomain_already_taken_handler(_request: Request, exc) -> JSONResponse:
    """Handle SubdomainAlreadyTaken exception"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
    )
