from __future__ import annotations

from tele2_trade import analyze


def test_fetch_lot_ids_parses_distinct_ids(monkeypatch):
    class FakeResponse:
        def json(self):
            return {"data": [{"id": 1}, {"id": 2}, {"id": 1}, {"id": 3}]}

        def raise_for_status(self):
            return None

    def fake_get(url, params=None, headers=None, timeout=None):
        assert params["trafficType"] == "voice"
        return FakeResponse()

    monkeypatch.setattr("tele2_trade.analyze.requests.get", fake_get)

    ids = analyze._fetch_lot_ids()
    assert ids == ["1", "2", "1", "3"]


def test_analyze_market_reports_unique_count_and_handles_errors(monkeypatch, caplog):
    calls = {"n": 0}

    class FakeResponse:
        def json(self):
            return {"data": [{"id": 1}, {"id": 2}]}

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
            if Stop.counter >= 3:
                raise KeyboardInterrupt

    with caplog.at_level("INFO", logger="tele2_trade.analyze"):
        try:
            analyze.analyze_market(interval_seconds=0, sleeper=Stop())
        except KeyboardInterrupt:
            pass

    assert any("Current distinct lots: 2" in r.message for r in caplog.records)
    assert any("Request failed" in r.message for r in caplog.records)