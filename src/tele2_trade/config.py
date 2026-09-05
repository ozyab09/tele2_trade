"""Application configuration.

Configuration is read from environment variables and validated on creation.
Keeping the config in a single dataclass removes the magic dicts that were
previously scattered across module-level code.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

from .errors import AuthError, ConfigError


@dataclass(frozen=True)
class LotTemplate:
    """Settings describing a single class of tradable lot."""

    traffic_type: str
    uom: str
    volume: int
    multiplier: float
    count: int
    defaults: dict = field(default_factory=dict)

    @property
    def offset_amount(self) -> int:
        """Whole rubles to charge, derived from the volume multiplier."""
        amount = self.volume * self.multiplier
        rounded = int(amount) if amount >= 0 else -int(-amount)
        return rounded if rounded >= 1 else 1


@dataclass(frozen=True)
class Config:
    """Validated runtime configuration for the bot."""

    phone: str
    token: str
    debug: bool
    types: dict[str, bool]
    templates: dict[str, LotTemplate]
    min_wait_seconds: int
    max_wait_seconds: int
    emoji_list: tuple[str, ...] = ("bomb", "cat", "cool", "devil", "rich", "scream", "tongue", "zipped")
    show_seller_names: tuple[str, ...] = ("true", "false")

    @classmethod
    def from_env(cls, env: Optional[dict] = None) -> "Config":
        """Build a :class:`Config` from environment variables (or ``env`` dict)."""
        env = os.environ if env is None else env

        phone = env.get("DEFAULT_PHONE") or env.get("default_phone") or ""
        token = env.get("DEFAULT_TOKEN") or env.get("default_token") or ""

        if not phone:
            raise AuthError("Missing DEFAULT_PHONE environment variable")
        if not token:
            raise AuthError("Missing DEFAULT_TOKEN environment variable")

        debug = env.get("DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}

        types = {
            "voice": _env_bool(env, "VOICE_ENABLED", False),
            "data": _env_bool(env, "DATA_ENABLED", False),
            "sms": _env_bool(env, "SMS_ENABLED", False),
        }

        templates = {
            "voice": LotTemplate(
                traffic_type="voice",
                uom="min",
                volume=_env_int(env, "VOICE_VOLUME", 50),
                multiplier=_env_float(env, "VOICE_MULTIPLIER", 0.8),
                count=_env_int(env, "VOICE_COUNT", 0),
                defaults={"uom": "min", "trafficType": "voice"},
            ),
            "data": LotTemplate(
                traffic_type="data",
                uom="gb",
                volume=_env_int(env, "DATA_VOLUME", 1),
                multiplier=_env_float(env, "DATA_MULTIPLIER", 15.0),
                count=_env_int(env, "DATA_COUNT", 0),
                defaults={"uom": "gb", "trafficType": "data"},
            ),
            "sms": LotTemplate(
                traffic_type="sms",
                uom="sms",
                volume=_env_int(env, "SMS_VOLUME", 50),
                multiplier=_env_float(env, "SMS_MULTIPLIER", 0.5),
                count=_env_int(env, "SMS_COUNT", 0),
                defaults={"uom": "sms", "trafficType": "sms"},
            ),
        }

        return cls(
            phone=phone,
            token=token,
            debug=debug,
            types=types,
            templates=templates,
            min_wait_seconds=_env_int(env, "MIN_WAIT_SECONDS", 80),
            max_wait_seconds=_env_int(env, "MAX_WAIT_SECONDS", 120),
        )

    def enabled_templates(self) -> list[LotTemplate]:
        """Return the templates whose type is enabled."""
        return [template for name, template in self.templates.items() if self.types[name]]

    def wait_range(self) -> tuple[int, int]:
        """Return the (min, max) polling interval in seconds."""
        if self.max_wait_seconds < self.min_wait_seconds:
            raise ConfigError("MAX_WAIT_SECONDS must be >= MIN_WAIT_SECONDS")
        return self.min_wait_seconds, self.max_wait_seconds


def _env_bool(env: dict, name: str, default: bool) -> bool:
    value = env.get(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(env: dict, name: str, default: int) -> int:
    value = env.get(name)
    if value is None or str(value).strip() == "":
        return default
    try:
        return int(value)
    except ValueError as exc:  # pragma: no cover - simple helper
        raise ConfigError(f"{name} must be an integer, got {value!r}") from exc


def _env_float(env: dict, name: str, default: float) -> float:
    value = env.get(name)
    if value is None or str(value).strip() == "":
        return default
    try:
        return float(value)
    except ValueError as exc:  # pragma: no cover - simple helper
        raise ConfigError(f"{name} must be a number, got {value!r}") from exc
