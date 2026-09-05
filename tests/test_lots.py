from __future__ import annotations

from tele2_trade.client import Tele2Client
from tele2_trade.config import Config


class _FakeClient(Tele2Client):
    """Tele2Client that records calls and serves canned responses."""

    def __init__(self, responses=None):
        super().__init__(phone="79012345678", token="test-token")
        self.responses = list(responses or [])
        self.responses_iter = iter(self.responses)
        self.calls = []

    def request(self, method, path, data=None, *, expected=200):
        self.calls.append((method.upper(), path, data))
        try:
            return next(self.responses_iter)
        except StopIteration:
            return {"data": {}}


def test_create_lot_creates_and_embellishes():
    client = _FakeClient(
        responses=[
            {"data": {"id": 42}},   # creation
            {"data": {}},           # embellishment (PATCH)
        ]
    )
    config = Config.from_env(
        {**{"DEFAULT_PHONE": "1", "DEFAULT_TOKEN": "t"}, "VOICE_ENABLED": "true", "VOICE_COUNT": "1"}
    )

    from tele2_trade.lots import create_lot

    create_lot(client, config, volume=50, amount=40, params={"uom": "min", "trafficType": "voice"})

    assert len(client.calls) == 2
    put_path, patch_path = client.calls[0][1], client.calls[1][1]
    assert put_path == "exchange/lots/created"
    assert patch_path == "exchange/lots/created/42"
    put_data = client.calls[0][2]
    assert put_data["cost"]["amount"] == "40"
    assert put_data["volume"] == {"value": "50", "uom": "min"}
    assert put_data["trafficType"] == "voice"
    patch_data = client.calls[1][2]
    assert len(patch_data["emojis"]) == 3
    assert patch_data["showSellerName"] in ("true", "false")


def test_create_lot_without_embellishment_when_no_id():
    client = _FakeClient(responses=[{"data": None}])
    config = Config.from_env(
        {**{"DEFAULT_PHONE": "1", "DEFAULT_TOKEN": "t"}, "VOICE_ENABLED": "true", "VOICE_COUNT": "1"}
    )

    from tele2_trade.lots import create_lot

    create_lot(client, config, volume=50, amount=40, params={"uom": "min", "trafficType": "voice"})
    assert len(client.calls) == 1


def test_get_lots_returns_only_active():
    client = _FakeClient(
        responses=[
            {
                "data": [
                    {"id": 1, "status": "active", "volume": {"value": 50, "uom": "min"},
                     "trafficType": "voice", "cost": {"amount": 40}},
                    {"id": 2, "status": "sold", "volume": {"value": 50, "uom": "min"},
                     "trafficType": "voice", "cost": {"amount": 40}},
                ]
            }
        ]
    )

    from tele2_trade.lots import get_lots

    lots = get_lots(client)
    assert len(lots) == 1
    assert lots[0]["id"] == 1
    assert lots[0]["trafficType"] == "voice"


def test_delete_current_lots_only_matching_type():
    client = _FakeClient(responses=[])

    from tele2_trade.lots import delete_current_lots

    lots = [
        {"id": 1, "volume": 50, "trafficType": "voice", "uom": "min", "amount": 40},
        {"id": 2, "volume": 1, "trafficType": "data", "uom": "gb", "amount": 15},
    ]
    delete_current_lots(client, "voice", lots)

    assert len(client.calls) == 1
    method, path, data = client.calls[0]
    assert method == "DELETE"
    assert path == "exchange/lots/created/1"
    assert data["trafficType"] == "voice"


def test_get_balance():
    client = _FakeClient(responses=[{"data": {"value": 100}}])

    from tele2_trade.lots import get_balance

    assert get_balance(client) == 100


def test_get_tariff_packages():
    client = _FakeClient(responses=[{"data": {"tariffPackages": [{"name": "x"}]}}])

    from tele2_trade.lots import get_tariff_packages

    assert get_tariff_packages(client) == [{"name": "x"}]


def test_get_tariff_packages_empty():
    client = _FakeClient(responses=[{"data": None}])

    from tele2_trade.lots import get_tariff_packages

    assert get_tariff_packages(client) == []