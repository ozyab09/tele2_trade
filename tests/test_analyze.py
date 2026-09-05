from __future__ import annotations

from tele2_trade import analyze


def test_fetch_cost_history_requests_new_endpoint(monkeypatch):
    captured = {}

    class FakeResponse:
        def json(self):
            return {"data": [{"cost": 40}, {"cost": 45}]}

        def raise_for_status(self):
            return None

    def fake_get(url, params=None, headers=None, timeout=None):
        captured["url"] = url
        captured["params"] = params
        return FakeResponse()

    monkeypatch.setattr("tele2_trade.analyze.requests.get", fake_get)

    body = analyze.fetch_cost_history("data")
    assert body["data"] == [{"cost": 40}, {"cost": 45}]
    assert captured["url"] == "https://msk.t2.ru/api/exchange/lots/stats/costs/history"
    assert captured["params"] == {"trafficType": "data"}


def test_history_points_extraction_variants():
    assert analyze._history_points({"data": [1, 2, 3]}) == [1, 2, 3]
    assert analyze._history_points({"data": {"history": [1]}}) == [1]
    assert analyze._history_points({"data": None}) == []
    assert analyze._history_points("not-a-dict") == []


def test_analyze_market_reports_and_handles_errors(monkeypatch, caplog):
    calls = {"n": 0}

    class FakeResponse:
        def json(self):
            return {"data": [{"cost": 40}, {"cost": 45}]}

        def raise_for_status(self):
            return None

    def fake_get(url, params=None, headers=None, timeout=None):
        calls["n"] += 1
        if calls["n"] == 2:
            raise analyze.requests.RequestException("timeout")
        return FakeResponse()

    monkeypatch.setattr("tele2_trade.analyze.requests.get", fake_get)

    class Stop:
        counter = 0

        def __call__(self, s):
            Stop.counter += 1
            if Stop.counter >= 2:
                raise KeyboardInterrupt

    with caplog.at_level("INFO", logger="tele2_trade.analyze"):
        try:
            analyze.analyze_market(interval_seconds=0, sleeper=Stop(), traffic_types=("data",))
        except KeyboardInterrupt:
            pass

    assert any("Cost history data: 2 points" in r.message for r in caplog.records)
    assert any("failed for data" in r.message for r in caplog.records)


def test_analyze_market_all_traffic_types(monkeypatch, caplog):
    class FakeResponse:
        def json(self):
            return {"data": [{"cost": 1}]}

        def raise_for_status(self):
            return None

    def fake_get(url, params=None, headers=None, timeout=None):
        return FakeResponse()

    monkeypatch.setattr("tele2_trade.analyze.requests.get", fake_get)

    class Stop:
        counter = 0

        def __call__(self, s):
            Stop.counter += 1
            if Stop.counter >= 1:
                raise KeyboardInterrupt

    with caplog.at_level("INFO", logger="tele2_trade.analyze"):
        try:
            analyze.analyze_market(interval_seconds=0, sleeper=Stop(), traffic_types=("data", "voice", "sms"))
        except KeyboardInterrupt:
            pass

    for t in ("data", "voice", "sms"):
        assert any(f"Cost history {t}: 1 points" in r.message for r in caplog.records)