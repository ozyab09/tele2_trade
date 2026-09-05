"""Market analyzer — tracks how many distinct lots are being offered."""

from __future__ import annotations

import json
import logging
import time
from typing import Callable

import requests

from .client import DEFAULT_USER_AGENT

logger = logging.getLogger(__name__)

MARKET_URL = "https://msk.tele2.ru/api/exchange/lots"


def _fetch_lot_ids(timeout: float = 30.0) -> list[str]:
    """Return the distinct lot ids currently listed for sale on the market."""
    params = {
        "trafficType": "voice",
        "volume": "50",
        "cost": "40",
        "offset": "0",
        "limit": "50",
    }
    response = requests.get(
        MARKET_URL,
        params=params,
        headers={"User-Agent": DEFAULT_USER_AGENT},
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json().get("data") or []
    return [str(item["id"]) for item in data]


def analyze_market(interval_seconds: float = 1.0, sleeper: Callable[[float], None] = time.sleep) -> None:
    """Continuously report the number of distinct lots on the market."""
    seen: set[str] = set()
    previous_count = 0

    while True:
        try:
            seen.update(_fetch_lot_ids())
            current_count = len(seen)
            if current_count != previous_count:
                previous_count = current_count
                logger.info("Current distinct lots: %s", current_count)
        except (requests.RequestException, json.JSONDecodeError):
            logger.warning("Request failed (timeout or API error)")
        sleeper(interval_seconds)


def main() -> None:
    """Entry point for the analyzer script."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    analyze_market()


if __name__ == "__main__":
    main()
