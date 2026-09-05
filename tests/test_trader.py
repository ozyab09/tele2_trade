from __future__ import annotations

import pytest

from tele2_trade.client import Tele2Client
from tele2_trade.config import Config
from tele2_trade.errors import ApiError
from tele2_trade.trader import Trader


class _FakeClient(Tele2Client):
    def __init__(self, balances, lots=None):
        super().__init__(phone="79012345678", token="test-token")
        self.balances = list(balances)
        self._last_balance = balances[0] if balances else 100
        self.fail_on = None
        self.lots = lots if lots is not None else []
        self.created = []

    def request(self, method, path, data=None, *, expected=200):
        if self.fail_on and self.fail_on(method, path):
            raise ApiError(400, "burst")
        if "balance" in path:
            if self.balances:
                self._last_balance = self.balances.pop(0)
            return {"data": {"value": self._last_balance}}
        if path == "exchange/lots/created" and method.upper() == "GET":
            return {"data": self.lots}
        if path.startswith("exchange/lots/created") and method.upper() == "DELETE":
            return {"data": None}
        if path == "exchange/lots/created" and method.upper() == "PUT":
            self.created.append((method, path, data))
            return {"data": {"id": 10}}
        if path.startswith("exchange/lots/created") and method.upper() == "PATCH":
            return {"data": None}
        if path == "siteMSK/rests":
            return {"data": {"tariffPackages": []}}
        raise AssertionError(f"Unexpected request: {method} {path}")


def _config(**overrides) -> Config:
    env = {
        "DEFAULT_PHONE": "1",
        "DEFAULT_TOKEN": "t",
        "VOICE_ENABLED": "true",
        "VOICE_COUNT": "1",
        "DATA_ENABLED": "false",
        "DATA_COUNT": "1",
        "SMS_ENABLED": "false",
        "SMS_COUNT": "1",
        "MIN_WAIT_SECONDS": "0",
        "MAX_WAIT_SECONDS": "0",
    }
    env.update(overrides)
    return Config.from_env(env)


class _StopAfter:
    """Sleeper that terminates the trading loop on the ``n``-th call."""

    def __init__(self, calls=1):
        self.calls = calls
        self.slept = []

    def __call__(self, seconds):
        self.slept.append(seconds)
        self.calls -= 1
        if self.calls < 0:
            raise KeyboardInterrupt


def test_run_creates_lots_and_sleeps():
    client = _FakeClient(balances=[100])
    stop = _StopAfter(calls=0)
    with pytest.raises(KeyboardInterrupt):
        Trader(client, _config(), sleeper=stop).run()

    assert len(client.created) == 1
    assert client.created[0][1] == "exchange/lots/created"
    assert stop.slept == [0]


def test_run_does_nothing_when_no_types_enabled(caplog):
    client = _FakeClient(balances=[100])
    stop = _StopAfter(calls=1)
    with caplog.at_level("INFO", logger="tele2_trade.trader"):
        Trader(client, _config(VOICE_ENABLED="false"), sleeper=stop).run()

    assert not client.created
    assert not stop.slept
    assert any("no lot types enabled" in r.message for r in caplog.records)


def test_balance_change_triggers_warning(caplog):
    client = _FakeClient(balances=[100, 90])
    stop = _StopAfter(calls=0)
    with pytest.raises(KeyboardInterrupt):
        Trader(client, _config(), sleeper=stop).run()

    assert any("Balance changed" in r.message for r in caplog.records)


def test_api_error_disables_type_and_stops_naturally():
    client = _FakeClient(balances=[100, 100])
    client.fail_on = lambda m, p: m.upper() == "PUT" and p == "exchange/lots/created"
    stop = _StopAfter(calls=5)
    trader = Trader(client, _config(), sleeper=stop)
    trader.run()

    assert not trader._active_types


def test_api_error_on_balance_crashes_run():
    client = _FakeClient(balances=[])
    client.fail_on = lambda m, p: "balance" in p

    stop = _StopAfter(calls=5)
    trader = Trader(client, _config(), sleeper=stop)

    with pytest.raises(ApiError):
        trader.run()


def test_multiple_enabled_types_all_created(caplog):
    client = _FakeClient(balances=[100])
    stop = _StopAfter(calls=0)
    with pytest.raises(KeyboardInterrupt):
        Trader(client, _config(DATA_ENABLED="true"), sleeper=stop).run()

    traffic_types = {c[2]["trafficType"] for c in client.created}
    assert traffic_types == {"voice", "data"}