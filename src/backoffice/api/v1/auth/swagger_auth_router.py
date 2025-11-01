from fastapi import APIRouter

from src.backoffice.apps.account.models import User
from src.backoffice.core.dependencies import AccountApplicationDep, BasicAuthUserDep

router = APIRouter(prefix="/swagger-auth", tags=["swagger-auth"])


@router.post("/login")
async def swagger_login(
    account_app: AccountApplicationDep, request_user: BasicAuthUserDep
):
    """
    Authorization via Swagger UI

    Enter your email and password in the Basic Auth form in Swagger UI
    This endpoint will return a JWT token for further use
    """
    user_model = User(
        id=request_user.id,
        email=request_user.email,
        username=request_user.username,
        first_name=request_user.first_name,
        last_name=request_user.last_name,
        is_active=request_user.is_active,
        is_verified=request_user.is_verified,
    )

    tokens = await account_app.create_tokens_for_user(user_model)

    return {
        "access_token": tokens.access_token,
        "token_type": "bearer",
        "user": {
            "id": request_user.id,
            "email": request_user.email,
            "username": request_user.username,
            "first_name": request_user.first_name,
            "last_name": request_user.last_name,
        },
    }
