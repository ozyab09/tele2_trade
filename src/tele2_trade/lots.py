"""Operations for managing market lots through the Tele2 API."""

from __future__ import annotations

import logging
import random
from typing import Any

from .client import Tele2Client
from .config import Config

logger = logging.getLogger(__name__)


def create_lot(client: Tele2Client, config: Config, volume: int, amount: int, params: dict[str, Any]) -> None:
    """Create a new lot and embellish it with an emoji / seller name."""
    data = {
        "volume": {"value": str(volume), "uom": params["uom"]},
        "cost": {"amount": str(amount), "currency": "rub"},
        "trafficType": params["trafficType"],
    }

    response = client.request("PUT", "exchange/lots/created", data)
    lot_id = (response.get("data") or {}).get("id")

    if lot_id:
        emojis = [random.choice(config.emoji_list) for _ in range(3)]
        update_data = {
            "showSellerName": random.choice(config.show_seller_names),
            "emojis": emojis,
            "cost": {"amount": str(amount), "currency": "rub"},
        }
        client.request("PATCH", f"exchange/lots/created/{lot_id}", update_data)

    logger.debug("Created %s lot: volume=%s, amount=%s", params["trafficType"], volume, amount)


def delete_lot(
    client: Tele2Client,
    volume: int,
    amount: int,
    lot_id: int,
    uom: str,
    traffic_type: str,
) -> None:
    """Delete a single lot by id."""
    data = {
        "volume": {"value": str(volume), "uom": uom},
        "cost": {"amount": str(amount), "currency": "rub"},
        "trafficType": traffic_type,
    }
    logger.debug("Deleting %s lot: volume=%s, amount=%s, id=%s", traffic_type, volume, amount, lot_id)
    client.request("DELETE", f"exchange/lots/created/{lot_id}", data)


def get_lots(client: Tele2Client, *, is_notify: bool = False) -> list[dict[str, Any]]:
    """Return the list of currently active lots."""
    response = client.request("GET", "exchange/lots/created")
    current_lots: list[dict[str, Any]] = []

    for item in response.get("data") or []:
        if item.get("status") == "active":
            current_lots.append(
                {
                    "id": item["id"],
                    "volume": item["volume"]["value"],
                    "trafficType": item["trafficType"],
                    "uom": item["volume"]["uom"],
                    "amount": item["cost"]["amount"],
                }
            )

    if is_notify:
        if current_lots:
            logger.info("Current lots:")
            for lot in current_lots:
                logger.info(
                    "%s: %s %s, %s rub.",
                    lot["trafficType"],
                    lot["volume"],
                    lot["uom"],
                    lot["amount"],
                )
        else:
            logger.info("No created lots")

    return current_lots


def delete_current_lots(client: Tele2Client, traffic_type: str, current_lots: list[dict[str, Any]]) -> None:
    """Delete every current lot matching ``traffic_type``."""
    logger.debug("Deleting %s lots", traffic_type)
    for lot in current_lots:
        if traffic_type == lot["trafficType"]:
            delete_lot(
                client,
                lot["volume"],
                lot["amount"],
                lot["id"],
                lot["uom"],
                lot["trafficType"],
            )


def get_balance(client: Tele2Client) -> int:
    """Return the current account balance in seconds/units."""
    response = client.request("GET", "balance")
    return int(response["data"]["value"])


def get_tariff_packages(client: Tele2Client) -> list:
    """Return the remaining tariff packages, if any."""
    response = client.request("GET", "siteMSK/rests")
    packages = (response.get("data") or {}).get("tariffPackages")
    if packages:
        logger.info("Tariff packages: %s", packages)
    return packages or []
