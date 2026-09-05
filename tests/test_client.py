from __future__ import annotations

import pytest

from tele2_trade.client import Tele2Client
from tele2_trade.errors import ApiError


def test_request_success(client, monkeypatch):
    captured = {}

    class FakeResponse:
        status_code = 200

        def json(self):
            return {"data": {"value": 123}}

    def fake_request(method, url, headers=None, data=None):
        captured["method"] = method
        captured["url"] = url
        captured["headers"] = headers
        captured["data"] = data
        return FakeResponse()

    monkeypatch.setattr("tele2_trade.client.requests.request", fake_request)
    result = client.request("GET", "balance")

    assert result == {"data": {"value": 123}}
    assert captured["method"].upper() == "GET"
    assert "79012345678" in captured["url"]
    assert captured["url"].endswith("/balance")
    assert captured["headers"]["Authorization"] == "Bearer test-token"


def test_request_forwards_payload(client, monkeypatch):
    captured = {}

    class FakeResponse:
        status_code = 200

        def json(self):
            return {}

    def fake_request(method, url, headers=None, data=None):
        captured["data"] = data
        return FakeResponse()

    monkeypatch.setattr("tele2_trade.client.requests.request", fake_request)
    client.request("PUT", "exchange/lots/created", {"volume": {"value": "50"}})

    assert captured["data"] == '{"volume": {"value": "50"}}'


def test_request_non_200_raises_api_error(client, monkeypatch):
    class FakeResponse:
        status_code = 500
        text = "boom"

        def json(self):
            raise ValueError("no json")

    def fake_request(method, url, headers=None, data=None):
        return FakeResponse()

    monkeypatch.setattr("tele2_trade.client.requests.request", fake_request)

    with pytest.raises(ApiError) as excinfo:
        client.request("GET", "balance")
    assert excinfo.value.status_code == 500
    assert "boom" in str(excinfo.value)


def test_error_message_extracted_from_meta(client, monkeypatch):
    class FakeResponse:
        status_code = 401
        text = "unauthorized"

        def json(self):
            return {"meta": {"message": "Invalid token"}}

    def fake_request(method, url, headers=None, data=None):
        return FakeResponse()

    monkeypatch.setattr("tele2_trade.client.requests.request", fake_request)

    with pytest.raises(ApiError) as excinfo:
        client.request("GET", "balance")
    assert "Invalid token" in str(excinfo.value)


def test_default_url_is_subscribers():
    client = Tele2Client(phone="p", token="t")
    assert client.base_url == "https://msk.t2.ru/api/subscribers"
    assert client.phone == "p"
    assert client.token == "t"


def test_base_url_trailing_slash_stripped():
    client = Tele2Client(phone="p", token="t", base_url="https://example.com/api/")
    assert client.base_url == "https://example.com/api"