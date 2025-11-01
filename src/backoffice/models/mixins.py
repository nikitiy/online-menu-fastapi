from datetime import datetime, timezone
from typing import Annotated, Tuple

from sqlalchemy import CheckConstraint, Constraint, DateTime, Integer, text
from sqlalchemy.orm import Mapped, declared_attr, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime as DateTimeType


class IdMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


UTCDateTime = Annotated[datetime, DateTimeType(timezone=True)]


class CreatedUpdatedMixin:
    created_at: Mapped[UTCDateTime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
        index=True,
        doc="When the record was created (UTC)",
    )
    updated_at: Mapped[UTCDateTime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        server_onupdate=func.now(),
        nullable=False,
        index=True,
        doc="When the entry was last updated (UTC)",
    )


class SingletonMixin:
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        default=1,
        server_default=text("1"),
    )

    @declared_attr
    def __table_args__(cls) -> Tuple[Constraint, ...]:  # noqa
        table_name = getattr(cls, "__tablename__", cls.__name__.lower())
        return (CheckConstraint("id = 1", name=f"ck_{table_name}_singleton"),)


__all__ = ("IdMixin", "CreatedUpdatedMixin", "SingletonMixin")
