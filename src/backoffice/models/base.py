from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

_NAMING_CONVENTION = {
    # indexes
    "ix": "ix_%(column_0_label)s",
    # unique constraints
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    # check constraints (prefer explicit names to be stable under Alembic)
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    # foreign keys
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    # primary keys
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=_NAMING_CONVENTION)

    def __repr__(self) -> str:  # pragma: no cover - trivial formatting
        cls_name = self.__class__.__name__
        try:
            parts: List[Tuple[str, object]] = []
            mapper = self.__mapper__  # type: ignore[attr-defined]

            show_pk: bool = getattr(self, "__repr_show_pk__", True)
            maxlen: int = getattr(self, "__repr_maxlen__", 80)
            configured_fields: Sequence[str] = tuple(
                getattr(self, "__repr_fields__", ())
            )

            pk_keys: List[str] = []
            if show_pk:
                pk_cols: Iterable = getattr(mapper, "primary_key", ())
                for col in pk_cols:
                    key = col.key
                    pk_keys.append(key)
                    parts.append((key, getattr(self, key, None)))

            columns = getattr(mapper, "columns", {})

            for key in configured_fields:
                if key in columns and key not in pk_keys:
                    parts.append((key, getattr(self, key, None)))

            def _fmt(value: object) -> str:
                if isinstance(value, str) and 0 < maxlen < len(value):
                    return repr(value[: maxlen - 1] + "…")
                return repr(value)

            inner = ", ".join(f"{k}={_fmt(v)}" for k, v in parts) if parts else "…"
            return f"<{cls_name}({inner})>"
        except (AttributeError, KeyError, TypeError):
            return f"<{cls_name}>"

    def __str__(self) -> str:  # pragma: no cover - trivial formatting
        return self.__repr__()


__all__ = ("Base",)
