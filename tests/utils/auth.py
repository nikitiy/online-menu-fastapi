import base64

from src.backoffice.apps.account.services.jwt_service import JWTService


def create_bearer_token(user_id: int, email: str) -> str:
    jwt_service = JWTService()
    token_data = {"user_id": user_id, "email": email}
    return jwt_service.create_access_token(token_data)


def create_refresh_token(user_id: int, email: str) -> str:
    jwt_service = JWTService()
    token_data = {"user_id": user_id, "email": email}
    return jwt_service.create_refresh_token(token_data)


def create_basic_auth_header(email: str, password: str) -> str:
    credentials = f"{email}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def create_bearer_auth_header(user_id: int, email: str) -> str:
    token = create_bearer_token(user_id, email)
    return f"Bearer {token}"
