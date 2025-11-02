import asyncio

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from src.backoffice.core.config import kafka_settings, s3_settings
from src.backoffice.core.dependencies.database import engine
from src.backoffice.core.services.kafka_client import kafka_client
from src.backoffice.core.services.s3_client import s3_client

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def liveness():
    return {"status": "ok"}


@router.get("/ready")
async def readiness():
    checks = {
        "database": False,
        "s3": False,
        "kafka": False,
    }

    errors = []

    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar()
        checks["database"] = True
    except Exception as e:
        errors.append(f"Database check failed: {str(e)}")

    if s3_settings.endpoint_url:
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: s3_client.s3_client.head_bucket(Bucket=s3_client.bucket_name),
            )
            checks["s3"] = True
        except Exception as e:
            checks["s3"] = False
            errors.append(f"S3 check failed: {str(e)}")

    if kafka_settings.get_bootstrap_servers():
        try:
            await kafka_client.get_producer()
            checks["kafka"] = True
        except Exception as e:
            checks["kafka"] = False
            errors.append(f"Kafka check failed: {str(e)}")

    if not checks["database"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "checks": checks,
                "errors": errors,
            },
        )

    return {
        "status": "ready",
        "checks": checks,
    }
