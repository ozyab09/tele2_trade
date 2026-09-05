from __future__ import annotations

import pytest

from tele2_trade.config import Config, LotTemplate
from tele2_trade.errors import AuthError


def test_from_env_builds_full_config(env):
    config = Config.from_env(env)
    assert config.phone == "79012345678"
    assert config.token == "test-token"
    assert config.debug is False
    assert config.types["voice"] is True
    assert config.types["data"] is True
    assert config.types["sms"] is False


def test_missing_phone_raises():
    with pytest.raises(AuthError):
        Config.from_env({"DEFAULT_TOKEN": "tok"})


def test_missing_token_raises():
    with pytest.raises(AuthError):
        Config.from_env({"DEFAULT_PHONE": "79012345678"})


def test_debug_parsing():
    assert Config.from_env({**{"DEFAULT_PHONE": "1", "DEFAULT_TOKEN": "t"}, "DEBUG": "True"}).debug
    assert Config.from_env({**{"DEFAULT_PHONE": "1", "DEFAULT_TOKEN": "t"}, "DEBUG": "false"}).debug is False


def test_enabled_templates_only(env):
    config = Config.from_env(env)
    enabled = config.enabled_templates()
    assert {t.traffic_type for t in enabled} == {"voice", "data"}


def test_legacy_env_vars_supported():
    config = Config.from_env({"default_phone": "1", "default_token": "t"})
    assert config.phone == "1"
    assert config.token == "t"


def test_wait_range_invalid():
    config = Config.from_env(
        {**{"DEFAULT_PHONE": "1", "DEFAULT_TOKEN": "t"}, "MIN_WAIT_SECONDS": "10", "MAX_WAIT_SECONDS": "5"}
    )
    with pytest.raises(Exception):
        config.wait_range()


def test_lot_template_offset_amount():
    template = LotTemplate(traffic_type="voice", uom="min", volume=50, multiplier=0.8, count=3)
    assert template.offset_amount == 40
    template = LotTemplate(traffic_type="data", uom="gb", volume=1, multiplier=15.0, count=3)
    assert template.offset_amount == 15