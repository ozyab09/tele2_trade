"""Command-line entry point for the Tele2 trading bot."""

from __future__ import annotations

import argparse
import logging
import sys

from .client import Tele2Client
from .config import Config
from .errors import ApiError, AuthError, ConfigError, Tele2Error


def _setup_logging(debug: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )


def build_config() -> Config:
    """Load and validate configuration from the environment."""
    try:
        config = Config.from_env()
        if config.debug:
            config.wait_range()
        return config
    except (ConfigError, AuthError) as exc:
        logging.error("Configuration error: %s", exc)
        raise


def main(argv: list[str] | None = None) -> int:
    """Run the trading bot. Returns the process exit code."""
    parser = argparse.ArgumentParser(description="Tele2 Stock Exchange trading bot")
    parser.add_argument("--analyze", action="store_true", help="run the market analyzer instead")
    args = parser.parse_args(argv)

    if args.analyze:
        from .analyze import analyze_market

        _setup_logging(False)
        logging.info("Starting market analyzer")
        analyze_market()
        return 0

    try:
        config = build_config()
    except (ConfigError, AuthError):
        return 1

    _setup_logging(config.debug)

    client = Tele2Client(phone=config.phone, token=config.token)

    from .trader import Trader

    try:
        Trader(client=client, config=config).run()
    except ApiError as exc:
        logging.error("API failure: %s", exc)
        return 1
    except Tele2Error as exc:
        logging.error("Application error: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
