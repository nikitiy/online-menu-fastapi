from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from src.backoffice.api.v1 import api_router
from src.backoffice.apps.company.exceptions import SubdomainAlreadyTaken
from src.backoffice.core.config import cors_settings, logging_settings
from src.backoffice.core.exceptions import subdomain_already_taken_handler
from src.backoffice.core.logging import configure_logging
from src.backoffice.core.middleware import AuthMiddleware, RequestContextMiddleware


def create_app() -> FastAPI:
    configure_logging(level=logging_settings.level, fmt=logging_settings.format)

    app = FastAPI(
        title="Backoffice API",
        description="API for backoffice management",
        version="0.1.0",
    )

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,  # type: ignore[attr-defined]
            version=app.version,  # type: ignore[attr-defined]
            description=app.description,  # type: ignore[attr-defined]
            routes=app.routes,
        )
        openapi_schema["components"]["securitySchemes"] = {
            "SwaggerAuth": {
                "type": "http",
                "scheme": "basic",
                "description": "Enter your email and password to log in via Swagger UI",
            },
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token obtained via /api/v1/auth/login",
            },
        }

        openapi_schema["security"] = [{"SwaggerAuth": []}, {"BearerAuth": []}]
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # Request context and auth middleware
    app.add_middleware(AuthMiddleware)
    app.add_middleware(RequestContextMiddleware)

    # Optional CORS
    if cors_settings.enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_settings.allow_origins,
            allow_credentials=cors_settings.allow_credentials,
            allow_methods=cors_settings.allow_methods,
            allow_headers=cors_settings.allow_headers,
        )

    # Exception handlers
    app.add_exception_handler(SubdomainAlreadyTaken, subdomain_already_taken_handler)

    # Routers
    app.include_router(api_router, prefix="/api/v1")

    return app


__all__ = ("create_app",)
