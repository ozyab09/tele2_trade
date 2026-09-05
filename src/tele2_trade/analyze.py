"""Market analyzer — polls the Tele2 exchange cost history per traffic type."""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Callable, Collection

import requests

from .client import DEFAULT_USER_AGENT

logger = logging.getLogger(__name__)

MARKET_STATS_URL = "https://msk.t2.ru/api/exchange/lots/stats/costs/history"
DEFAULT_TRAFFIC_TYPES = ("data", "voice", "sms")


def fetch_cost_history(traffic_type: str, timeout: float = 30.0) -> dict:
    """Return the raw cost history payload for the given traffic type."""
    response = requests.get(
        MARKET_STATS_URL,
        params={"trafficType": traffic_type},
        headers={"User-Agent": DEFAULT_USER_AGENT},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def _history_points(body: Any) -> list:
    """Best-effort extraction of the cost-history point list from a payload."""
    if not isinstance(body, dict):
        return []
    data = body.get("data")
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("history", "costs", "points", "items"):
            if isinstance(data.get(key), list):
                return data[key]
    return [data] if data is not None else []


def analyze_market(
    interval_seconds: float = 1.0,
    sleeper: Callable[[float], None] = time.sleep,
    traffic_types: Collection[str] = DEFAULT_TRAFFIC_TYPES,
) -> None:
    """Continuously report the cost-history size for each traffic type."""
    while True:
        for traffic_type in traffic_types:
            try:
                points = _history_points(fetch_cost_history(traffic_type))
                logger.info("Cost history %s: %s points", traffic_type, len(points))
            except (requests.RequestException, json.JSONDecodeError):
                logger.warning("Cost history request failed for %s (timeout or API error)", traffic_type)
        sleeper(interval_seconds)


def main() -> None:
    """Entry point for the analyzer script."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    analyze_market()


if __name__ == "__main__":
    main()