"""Domain-specific exceptions for the Tele2 trading bot."""


class Tele2Error(Exception):
    """Base exception for all tele2_trade errors."""


class ConfigError(Tele2Error):
    """Raised when the configuration is invalid or incomplete."""


class AuthError(Tele2Error):
    """Raised when authentication / token information is missing."""


class ApiError(Tele2Error):
    """Raised when the Tele2 API returns an unexpected or failing response."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"API error {status_code}: {message}")
