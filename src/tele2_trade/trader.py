"""The main trading orchestration loop."""

from __future__ import annotations

import logging
import math
import random
import time
from typing import Callable

from .client import Tele2Client
from .config import Config
from .lots import create_lot, delete_current_lots, get_balance, get_lots

logger = logging.getLogger(__name__)


class Trader:
    """Runs the core trading cycle until all lot types are exhausted."""

    def __init__(
        self,
        client: Tele2Client,
        config: Config,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.client = client
        self.config = config
        self._sleep = sleeper
        self._active_types = {t.traffic_type for t in config.enabled_templates()}

    def run(self) -> None:
        """Run the trading loop.

        The loop reconciles the market lots with the configured targets and
        stops as soon as every enabled lot type has been fully processed.
        """
        if not self._active_types:
            logger.info("Finished: no lot types enabled")
            return

        min_wait, max_wait = self.config.wait_range()

        start_balance = self.get_balance()
        previous_balance = start_balance
        logger.info("Trading started. Current balance: %s", start_balance)

        while self._active_types:
            current_balance = self.get_balance()
            if current_balance != previous_balance:
                logger.warning(
                    "Balance changed: current=%s start=%s difference=%s",
                    current_balance,
                    start_balance,
                    current_balance - start_balance,
                )
                previous_balance = current_balance

            current_lots = get_lots(self.client)

            for traffic_type in list(self._active_types):
                template = self.config.templates[traffic_type]
                amount = math.ceil(template.volume * template.multiplier)

                delete_current_lots(self.client, traffic_type, current_lots)

                for attempt in range(template.count):
                    try:
                        create_lot(
                            self.client,
                            self.config,
                            template.volume,
                            amount,
                            {"uom": template.uom, "trafficType": traffic_type},
                        )
                    except Exception:
                        logger.info(
                            "Error creating %s lot, try #%s",
                            traffic_type,
                            attempt + 1,
                            exc_info=True,
                        )
                        self._active_types.discard(traffic_type)
                        break

            wait_time = random.randint(min_wait, max_wait)
            logger.debug("Waiting %s seconds", wait_time)
            self._sleep(wait_time)

        logger.info("Finished")

    def get_balance(self) -> int:
        """Return the current account balance, raising on API failure."""
        return get_balance(self.client)
