from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.backoffice.core.config import auth_settings


class JWTService:
    def __init__(self):
        self.secret_key = auth_settings.secret_key
        self.algorithm = auth_settings.algorithm
        self.access_token_expire_minutes = auth_settings.access_token_expire_minutes
        self.refresh_token_expire_days = auth_settings.refresh_token_expire_days
        self.pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=self.refresh_token_expire_days
            )

        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> Optional[dict]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                return None
            return payload
        except JWTError:
            return None

    def verify_access_token(self, token: str) -> Optional[dict]:
        return self.verify_token(token, "access")

    def verify_refresh_token(self, token: str) -> Optional[dict]:
        return self.verify_token(token, "refresh")

    def get_user_id_from_token(self, token: str) -> Optional[int]:
        payload = self.verify_access_token(token)
        if payload:
            return payload.get("user_id")
        return None

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)


jwt_service = JWTService()
