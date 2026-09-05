from __future__ import annotations

from tele2_trade import __main__ as entry


def test_main_missing_config_returns_1(caplog, monkeypatch):
    def bad_from_env():
        from tele2_trade.errors import AuthError

        raise AuthError("Missing DEFAULT_PHONE environment variable")

    monkeypatch.setattr(entry.Config, "from_env", staticmethod(bad_from_env))

    with caplog.at_level("ERROR", logger="tele2_trade.__main__"):
        code = entry.main([])

    assert code == 1
    assert any("Missing DEFAULT_PHONE" in r.message for r in caplog.records)


def test_main_analyze_flag(monkeypatch):
    called = {}

    def fake_analyze():
        called["hit"] = True

    import tele2_trade.analyze as analyze_mod

    monkeypatch.setattr(analyze_mod, "analyze_market", fake_analyze)
    code = entry.main(["--analyze"])
    assert code == 0
    assert called["hit"] is True


def test_build_config_rejects_invalid_number(monkeypatch, caplog):
    monkeypatch.setattr(
        entry.Config,
        "from_env",
        staticmethod(lambda: (_ for _ in ()).throw(entry.ConfigError("MIN_WAIT_SECONDS must be an integer"))),
    )
    with caplog.at_level("ERROR", logger="tele2_trade.__main__"):
        code = entry.main([])
    assert code == 1


def test_main_returns_1_on_api_error(monkeypatch, caplog):
    valid_env = {"DEFAULT_PHONE": "1", "DEFAULT_TOKEN": "t", "VOICE_ENABLED": "false"}
    original_from_env = entry.Config.from_env
    monkeypatch.setattr(entry.Config, "from_env", staticmethod(lambda: original_from_env(valid_env)))
    monkeypatch.setattr(entry.Tele2Client, "__init__", lambda self, **kwargs: None)

    def fail_forever(*args, **kwargs):
        raise entry.ApiError(503, "service down")

    import tele2_trade.trader as trader_mod

    class _BrokenTrader:
        def __init__(self, client, config):
            pass

        run = staticmethod(fail_forever)

    monkeypatch.setattr(trader_mod, "Trader", _BrokenTrader)

    with caplog.at_level("ERROR", logger="tele2_trade.__main__"):
        code = entry.main([])
    assert code == 1
    assert any("API failure" in r.message for r in caplog.records)