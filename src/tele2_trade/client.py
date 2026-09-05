"""HTTP transport for the Tele2 exchange API.

Encapsulates URL building, headers and request marshalling so that the rest of
the code deals with API semantics rather than raw ``requests`` calls.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

import requests

from .errors import ApiError

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
)


class Tele2Client:
    """Thin authenticated client for the Tele2 exchange API."""

    def __init__(self, phone: str, token: str, base_url: str = "https://msk.tele2.ru/api/subscribers") -> None:
        self.phone = phone
        self.token = token
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": DEFAULT_USER_AGENT,
        }

    def request(
        self,
        method: str,
        path: str,
        data: Optional[dict] = None,
        *,
        expected: int = 200,
    ) -> dict:
        """Perform a request against the API and parse the JSON response body.

        :raises ApiError: when the HTTP status does not match ``expected``.
        """
        url = f"{self.base_url}/{self.phone}/{path.lstrip('/')}"
        payload = json.dumps(data) if data is not None else None
        logger.debug("%s %s", method.upper(), url)

        response = requests.request(method, url, headers=self._headers(), data=payload)

        if response.status_code != expected:
            message = _extract_message(response)
            raise ApiError(response.status_code, message)

        try:
            return response.json()
        except ValueError as exc:  # pragma: no cover - defensive
            raise ApiError(response.status_code, "Response is not valid JSON") from exc


def _extract_message(response: "requests.Response") -> str:
    """Best-effort extraction of an error message from an API response."""
    try:
        body = response.json()
    except ValueError:
        return response.text or f"HTTP {response.status_code}"
    meta = body.get("meta", {}) if isinstance(body, dict) else {}
    return str(meta.get("message") or body or f"HTTP {response.status_code}")
