import base64
import uuid
from typing import Optional

from fastapi import Request
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

from src.backoffice.apps.account.schemas import UserProfile
from src.backoffice.apps.account.services import UserService, jwt_service
from src.backoffice.apps.account.utils import verify_password
from src.backoffice.core.context import request_id_ctx_var, user_id_ctx_var
from src.backoffice.core.dependencies import get_session
from src.backoffice.core.logging import get_logger


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts user info from JWT token and sets it in context.
    Also checks authentication requirements based on route decorators.
    """

    def __init__(self, app):
        super().__init__(app)
        self.security = HTTPBearer(auto_error=False)
        self.logger = get_logger("auth")

    async def dispatch(self, request: Request, call_next):
        user = await self._extract_user_from_token(request)

        request.state.user_id = user.id if user else None
        request.state.user_email = user.email if user else None

        return await call_next(request)

    async def _extract_user_from_token(self, request: Request) -> Optional[UserProfile]:
        try:
            authorization = request.headers.get("authorization")

            if authorization and authorization.startswith("Bearer "):
                token = authorization.split(" ")[1]
                payload = jwt_service.verify_access_token(token)
                if payload:
                    user_id = payload.get("user_id")
                    if user_id:
                        try:
                            async for session in get_session():
                                user_service = UserService(session)
                                user = await user_service.get_by_id(user_id)
                                if user and user.is_active:
                                    return UserProfile.model_validate(user)
                                break
                        except Exception as e:
                            self.logger.warning(
                                "Error getting user from database", exc_info=e
                            )
                            return None

            if authorization and authorization.startswith("Basic "):

                try:
                    encoded_credentials = authorization.split(" ")[1]
                    decoded_credentials = base64.b64decode(encoded_credentials).decode(
                        "utf-8"
                    )
                    username, password = decoded_credentials.split(":", 1)

                    try:
                        async for session in get_session():
                            user_service = UserService(session)
                            user = await user_service.get_by_email(username)
                            if user and user.is_active and user.password_hash:
                                if verify_password(password, str(user.password_hash)):
                                    return UserProfile.model_validate(user)
                            break
                    except Exception as e:
                        self.logger.warning("Error verifying Basic Auth", exc_info=e)
                        return None
                except Exception as e:
                    self.logger.warning("Error decoding Basic Auth", exc_info=e)
                    return None

            return None

        except Exception as e:
            self.logger.warning("Error extracting user from token", exc_info=e)
            return None


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Assigns request_id and sets context variables"""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        token = request_id_ctx_var.set(request_id)
        user_token = user_id_ctx_var.set("-")

        try:
            response = await call_next(request)
        finally:
            request_id_ctx_var.reset(token)
            user_id_ctx_var.reset(user_token)

        return response
