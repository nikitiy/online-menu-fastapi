import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class DBSettings:
    def __init__(self):
        self.host = os.environ["SQL_HOST"]
        self.port = os.environ["SQL_PORT"]
        self.database = os.environ["SQL_DATABASE"]
        self.user = os.environ["SQL_USER"]
        self.password = os.environ["SQL_PASSWORD"]
        self.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-here")
        self.algorithm = os.environ.get("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(
            os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )
        self.refresh_token_expire_days = int(
            os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7")
        )

    @property
    def ASYNC_DATABASE_URL(self) -> str:  # noqa
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def SYNC_DATABASE_URL(self) -> str:  # noqa
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class GeocodingSettings:
    def __init__(self):
        # Google Maps API
        self.google_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        self.google_base_url = "https://maps.googleapis.com/maps/api/geocode/json"

        # Yandex Maps API
        self.yandex_api_key = os.environ.get("YANDEX_MAPS_API_KEY")
        self.yandex_base_url = "https://geocode-maps.yandex.ru/1.x"

        # OpenStreetMap Nominatim
        self.nominatim_base_url = "https://nominatim.openstreetmap.org"
        self.nominatim_user_agent = os.environ.get(
            "NOMINATIM_USER_AGENT", "BackofficeGeocoder/1.0"
        )

        # Mapbox API
        self.mapbox_api_key = os.environ.get("MAPBOX_API_KEY")
        self.mapbox_base_url = "https://api.mapbox.com/geocoding/v5"

        # Base settings
        self.default_provider = os.environ.get("DEFAULT_GEOCODING_PROVIDER", "google")
        self.cache_ttl = int(os.environ.get("GEOCODING_CACHE_TTL", "86400"))  # 24 hours
        self.rate_limit_requests = int(os.environ.get("GEOCODING_RATE_LIMIT", "100"))
        self.rate_limit_period = int(
            os.environ.get("GEOCODING_RATE_PERIOD", "3600")
        )  # 1 hour
        self.timeout = int(os.environ.get("GEOCODING_TIMEOUT", "10"))  # 10 seconds
        self.max_retries = int(os.environ.get("GEOCODING_MAX_RETRIES", "3"))

        # Settings for different providers
        self.providers_config = {
            "google": {
                "enabled": bool(self.google_api_key),
                "api_key": self.google_api_key,
                "base_url": self.google_base_url,
                "rate_limit": 2500,  # requests per day
                "timeout": self.timeout,
            },
            "yandex": {
                "enabled": bool(self.yandex_api_key),
                "api_key": self.yandex_api_key,
                "base_url": self.yandex_base_url,
                "rate_limit": 1000,  # requests per day
                "timeout": self.timeout,
            },
            "nominatim": {
                "enabled": True,  # free
                "base_url": self.nominatim_base_url,
                "user_agent": self.nominatim_user_agent,
                "rate_limit": 1,  # requests per day
                "timeout": self.timeout,
            },
            "mapbox": {
                "enabled": bool(self.mapbox_api_key),
                "api_key": self.mapbox_api_key,
                "base_url": self.mapbox_base_url,
                "rate_limit": 100000,  # requests per day
                "timeout": self.timeout,
            },
        }

    def get_provider_config(self, provider: str) -> Optional[dict]:
        return self.providers_config.get(provider)

    def is_provider_enabled(self, provider: str) -> bool:
        config = self.get_provider_config(provider)
        return config and config.get("enabled", False)


class AuthSettings:
    def __init__(self):
        # JWT settings
        self.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-here")
        self.algorithm = os.environ.get("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(
            os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )
        self.refresh_token_expire_days = int(
            os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7")
        )

        # Google OAuth
        self.google_client_id = os.environ.get("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
        self.google_redirect_uri = os.environ.get(
            "GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/google/callback"
        )

        # Yandex OAuth
        self.yandex_client_id = os.environ.get("YANDEX_CLIENT_ID")
        self.yandex_client_secret = os.environ.get("YANDEX_CLIENT_SECRET")
        self.yandex_redirect_uri = os.environ.get(
            "YANDEX_REDIRECT_URI", "http://localhost:8000/api/v1/auth/yandex/callback"
        )

        # VK OAuth
        self.vk_client_id = os.environ.get("VK_CLIENT_ID")
        self.vk_client_secret = os.environ.get("VK_CLIENT_SECRET")
        self.vk_redirect_uri = os.environ.get(
            "VK_REDIRECT_URI", "http://localhost:8000/api/v1/auth/vk/callback"
        )

        # Base settings
        self.frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
        self.backend_url = os.environ.get("BACKEND_URL", "http://localhost:8000")


class S3Settings:
    def __init__(self):
        # MinIO/S3 settings
        self.endpoint_url = os.environ.get("MINIO_ENDPOINT", "http://localhost:9000")
        self.access_key = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.environ.get("MINIO_SECRET_KEY", "minioadmin123")
        self.bucket_name = os.environ.get("MINIO_BUCKET_NAME", "menu-images")
        self.region = os.environ.get("MINIO_REGION", "us-east-1")

        # File upload settings
        self.max_file_size = int(os.environ.get("MAX_FILE_SIZE", "10485760"))  # 10MB
        self.allowed_extensions = os.environ.get(
            "ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif,webp,bmp,svg"
        ).split(",")
        self.allowed_mime_types = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "image/bmp",
            "image/svg+xml",
        ]

        # Image processing settings
        self.generate_thumbnails = (
            os.environ.get("GENERATE_THUMBNAILS", "true").lower() == "true"
        )
        self.thumbnail_sizes = [
            (150, 150),  # Small thumbnail
            (300, 300),  # Medium thumbnail
            (600, 600),  # Large thumbnail
        ]
        self.max_image_dimensions = (2048, 2048)

        # Security settings
        self.use_https = os.environ.get("MINIO_USE_HTTPS", "false").lower() == "true"
        self.presigned_url_expiry = int(
            os.environ.get("PRESIGNED_URL_EXPIRY", "3600")
        )  # 1 hour


class KafkaSettings:
    def __init__(self):
        # List of brokers in the format host:port,host:port
        self.brokers = os.environ.get(
            "KAFKA_BROKERS", os.environ.get("TEST_KAFKA_BROKERS", "")
        ).split(",")
        self.client_id = os.environ.get("KAFKA_CLIENT_ID", "backoffice-app")

        # Optional security settings (for production environments)
        self.security_protocol = os.environ.get(
            "KAFKA_SECURITY_PROTOCOL"
        )  # eg. SASL_SSL
        self.sasl_mechanism = os.environ.get("KAFKA_SASL_MECHANISM")  # eg. PLAIN
        self.sasl_username = os.environ.get("KAFKA_SASL_USERNAME")
        self.sasl_password = os.environ.get("KAFKA_SASL_PASSWORD")

        # Test/internal settings
        self.topic_prefix = os.environ.get("KAFKA_TOPIC_PREFIX", "")

    def get_bootstrap_servers(self) -> list[str]:
        return [b for b in self.brokers if b]


class LoggingSettings:
    def __init__(self):
        # Logging level: DEBUG/INFO/WARNING/ERROR
        self.level = os.environ.get("LOG_LEVEL", "INFO")
        # Format: json or text
        self.format = os.environ.get("LOG_FORMAT", "json")
        # Enable request/response logging
        self.log_requests = os.environ.get("LOG_REQUESTS", "true").lower() == "true"
        # Request/response body size limit for logs (in bytes)
        self.body_limit = int(os.environ.get("LOG_BODY_LIMIT", "4096"))


class CorsSettings:
    def __init__(self):
        self.enabled = os.environ.get("CORS_ENABLED", "true").lower() == "true"
        self.allow_origins = os.environ.get("CORS_ALLOW_ORIGINS", "*").split(",")
        self.allow_credentials = (
            os.environ.get("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
        )
        self.allow_methods = os.environ.get("CORS_ALLOW_METHODS", "*").split(",")
        self.allow_headers = os.environ.get("CORS_ALLOW_HEADERS", "*").split(",")


db_settings = DBSettings()
geocoding_settings = GeocodingSettings()
auth_settings = AuthSettings()
s3_settings = S3Settings()
kafka_settings = KafkaSettings()
logging_settings = LoggingSettings()
cors_settings = CorsSettings()
