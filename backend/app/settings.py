from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from os import getenv


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_int(value: str | None, default: int) -> int:
    if value is None or value.strip() == "":
        return default
    return int(value)


def _parse_list(value: str | None, default: Sequence[str]) -> list[str]:
    if value is None or value.strip() == "":
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_host: str
    app_port: int
    uvicorn_reload: bool
    cors_origins: list[str]


def get_settings() -> Settings:
    return Settings(
        app_host=getenv("APP_HOST", "127.0.0.1"),
        app_port=_parse_int(getenv("APP_PORT"), 8000),
        uvicorn_reload=_parse_bool(getenv("UVICORN_RELOAD"), False),
        cors_origins=_parse_list(
            getenv("CORS_ORIGINS"),
            ("http://localhost:3000", "http://127.0.0.1:3000"),
        ),
    )


settings = get_settings()
