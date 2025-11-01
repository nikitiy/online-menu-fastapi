import base64
from typing import Annotated, TypeAlias

from fastapi import Depends, HTTPException, Request, status

from src.backoffice.apps.account.schemas import UserProfile
from src.backoffice.apps.account.services import UserService, jwt_service
from src.backoffice.apps.account.utils import verify_password
from src.backoffice.core.dependencies.database import SessionDep


async def get_request_user_any_auth(
    request: Request,
    session: SessionDep,
) -> UserProfile:
    """Get request user from either Basic Auth or Bearer token"""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        user_service = UserService(session)
        user = await user_service.get_by_id(user_id)
        if user and user.is_active:
            return UserProfile.model_validate(user)

    authorization = request.headers.get("authorization")

    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = jwt_service.verify_access_token(token)
        if payload:
            user_id = payload.get("user_id")
            if user_id:
                user_service = UserService(session)
                user = await user_service.get_by_id(user_id)
                if user and user.is_active:
                    return UserProfile.model_validate(user)

    if authorization and authorization.startswith("Basic "):
        try:
            encoded_credentials = authorization.split(" ")[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            username, password = decoded_credentials.split(":", 1)

            user_service = UserService(session)
            user = await user_service.get_by_email(username)

            if not user or not user.is_active or not user.password_hash:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Basic, Bearer"},
                )

            if not verify_password(password, str(user.password_hash)):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Basic, Bearer"},
                )

            return UserProfile.model_validate(user)
        except (ValueError, IndexError):
            # Invalid Basic Auth encoding, will fall through to raise 401
            pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Basic, Bearer"},
    )


AnyAuthUserDep: TypeAlias = Annotated[UserProfile, Depends(get_request_user_any_auth)]
