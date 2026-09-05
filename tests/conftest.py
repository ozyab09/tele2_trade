"""Shared fixtures for the test-suite."""

from __future__ import annotations

import pytest

from tele2_trade.client import Tele2Client
from tele2_trade.config import Config


@pytest.fixture
def env() -> dict:
    return {
        "DEFAULT_PHONE": "79012345678",
        "DEFAULT_TOKEN": "test-token",
        "VOICE_ENABLED": "true",
        "DATA_ENABLED": "true",
        "SMS_ENABLED": "false",
        "VOICE_COUNT": "2",
        "DATA_COUNT": "3",
        "SMS_COUNT": "1",
    }


@pytest.fixture
def config(env) -> Config:
    return Config.from_env(env)


@pytest.fixture
def client() -> Tele2Client:
    return Tele2Client(phone="79012345678", token="test-token")