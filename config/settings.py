from dataclasses import dataclass
from os import getenv
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


DEFAULT_TOKEN_FILE = "auth/gmail_token.json"
DEFAULT_OTP_REGEX = r"Verification Details:\s*(\d{6})"
DEFAULT_OTP_TIMEOUT_SECONDS = 90.0
DEFAULT_OTP_POLL_INTERVAL_SECONDS = 3.0
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def get_target_base_url() -> str:
    """Empty when unset so callers can fall back to their own default."""
    return getenv("E2E_BASE_URL", "").rstrip("/")


@dataclass(frozen=True)
class GmailSettings:
    client_id: str | None
    client_secret: str | None
    refresh_token: str | None
    client_secret_file: str | None
    token_file: str
    otp_regex: str
    otp_timeout_seconds: float
    otp_poll_interval_seconds: float


def _float_setting(name: str, default: float) -> float:
    value = getenv(name)
    if not value:
        return default
    try:
        return float(value)
    except ValueError as error:
        raise ValueError(f"{name} must be a number, got {value!r}") from error


def _resolve_path_setting(value: str | None) -> str | None:
    if not value:
        return None
    path = Path(value)
    return str(path if path.is_absolute() else PROJECT_ROOT / path)


def get_gmail_settings() -> GmailSettings:
    return GmailSettings(
        client_id=getenv("GMAIL_CLIENT_ID"),
        client_secret=getenv("GMAIL_CLIENT_SECRET"),
        refresh_token=getenv("GMAIL_REFRESH_TOKEN"),
        client_secret_file=_resolve_path_setting(getenv("GMAIL_CLIENT_SECRET_FILE")),
        token_file=_resolve_path_setting(getenv("GMAIL_TOKEN_FILE", DEFAULT_TOKEN_FILE))
        or str(PROJECT_ROOT / DEFAULT_TOKEN_FILE),
        otp_regex=getenv("OTP_REGEX", DEFAULT_OTP_REGEX),
        otp_timeout_seconds=_float_setting(
            "OTP_TIMEOUT_SECONDS", DEFAULT_OTP_TIMEOUT_SECONDS
        ),
        otp_poll_interval_seconds=_float_setting(
            "OTP_POLL_INTERVAL_SECONDS", DEFAULT_OTP_POLL_INTERVAL_SECONDS
        ),
    )


def is_ci() -> bool:
    return bool(getenv("CI"))