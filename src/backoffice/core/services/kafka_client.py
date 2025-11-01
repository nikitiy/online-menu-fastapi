from __future__ import annotations

import asyncio
import contextlib
from typing import Any, AsyncIterator, Callable, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from src.backoffice.core.config import kafka_settings
from src.backoffice.core.logging import get_logger


class KafkaClient:
    def __init__(self):
        self._producer: Optional[AIOKafkaProducer] = None
        self._producer_lock = asyncio.Lock()
        self._logger = get_logger("kafka")

    async def get_producer(self) -> AIOKafkaProducer:
        if self._producer is not None:
            return self._producer
        async with self._producer_lock:
            if self._producer is None:
                self._logger.info(
                    "kafka_producer_initializing",
                    extra={"brokers": kafka_settings.get_bootstrap_servers()},
                )
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=kafka_settings.get_bootstrap_servers(),
                    client_id=kafka_settings.client_id,
                    security_protocol=kafka_settings.security_protocol,
                    sasl_mechanism=kafka_settings.sasl_mechanism,
                    sasl_plain_username=kafka_settings.sasl_username,
                    sasl_plain_password=kafka_settings.sasl_password,
                )
                await self._producer.start()
                self._logger.info("kafka_producer_started")
        return self._producer

    async def stop(self):
        if self._producer is not None:
            await self._producer.stop()
            self._logger.info("kafka_producer_stopped")
            self._producer = None

    async def send(
        self, topic: str, value: bytes, key: Optional[bytes] = None, **kwargs: Any
    ):
        topic_name = f"{kafka_settings.topic_prefix}{topic}"
        producer = await self.get_producer()
        await producer.send_and_wait(topic_name, value=value, key=key, **kwargs)
        self._logger.info(
            "kafka_message_sent",
            extra={
                "topic": topic_name,
                "key": (key.decode() if isinstance(key, (bytes, bytearray)) else None),
                "size": len(value) if value else 0,
            },
        )

    async def consume(
        self,
        topic: str,
        group_id: str,
        handler: Callable[[bytes, Optional[bytes]], Any],
        *,
        auto_offset_reset: str = "earliest",
    ) -> AsyncIterator[None]:
        topic_name = f"{kafka_settings.topic_prefix}{topic}"
        consumer = AIOKafkaConsumer(
            topic_name,
            bootstrap_servers=kafka_settings.get_bootstrap_servers(),
            group_id=group_id,
            client_id=kafka_settings.client_id,
            auto_offset_reset=auto_offset_reset,
            security_protocol=kafka_settings.security_protocol,
            sasl_mechanism=kafka_settings.sasl_mechanism,
            sasl_plain_username=kafka_settings.sasl_username,
            sasl_plain_password=kafka_settings.sasl_password,
        )
        await consumer.start()
        self._logger.info(
            "kafka_consumer_started", extra={"topic": topic_name, "group_id": group_id}
        )

        async def _runner():
            try:
                async for msg in consumer:
                    await handler(msg.value, msg.key)
                    self._logger.debug(
                        "kafka_message_consumed",
                        extra={
                            "topic": topic_name,
                            "partition": msg.partition,
                            "offset": msg.offset,
                        },
                    )
            finally:
                await consumer.stop()
                self._logger.info(
                    "kafka_consumer_stopped",
                    extra={"topic": topic_name, "group_id": group_id},
                )

        task = asyncio.create_task(_runner())
        try:
            yield None
        finally:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task


kafka_client = KafkaClient()
