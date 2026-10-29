"""Resolves Gmail API credentials without ever driving the Gmail UI."""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config.settings import GmailSettings, get_gmail_settings, is_ci


GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPES = [GMAIL_READONLY_SCOPE]


class GmailAuthUnavailable(RuntimeError):
    """Raised when no usable Gmail OAuth credential can be resolved."""


def resolve_credentials(settings: GmailSettings | None = None) -> Credentials:
    settings = settings or get_gmail_settings()

    credentials = _from_refresh_token(settings) or _from_token_file(settings)
    if credentials:
        return credentials

    if is_ci():
        raise GmailAuthUnavailable(
            "No Gmail credentials in CI. Provide GMAIL_CLIENT_ID, "
            "GMAIL_CLIENT_SECRET and GMAIL_REFRESH_TOKEN as secrets "
            "(generate them with scripts/gmail_bootstrap.py)."
        )
    return run_interactive_consent(settings)


def _from_refresh_token(settings: GmailSettings) -> Credentials | None:
    if not (settings.client_id and settings.client_secret and settings.refresh_token):
        return None
    credentials = Credentials(
        token=None,
        refresh_token=settings.refresh_token,
        token_uri=TOKEN_URI,
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        scopes=SCOPES,
    )
    _refresh(credentials)
    return credentials


def _from_token_file(settings: GmailSettings) -> Credentials | None:
    token_file = Path(settings.token_file)
    if not token_file.exists():
        return None
    credentials = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    if not credentials.valid:
        if not credentials.refresh_token:
            return None
        _refresh(credentials)
        save_credentials(credentials, token_file)
    return credentials


def run_interactive_consent(settings: GmailSettings) -> Credentials:
    if not settings.client_secret_file:
        raise GmailAuthUnavailable(
            "Set GMAIL_CLIENT_SECRET_FILE to a Google OAuth desktop client secret "
            "JSON file, then run scripts/gmail_bootstrap.py."
        )
    client_secret_file = Path(settings.client_secret_file)
    if not client_secret_file.exists():
        raise GmailAuthUnavailable(
            f"GMAIL_CLIENT_SECRET_FILE points at a missing file: {client_secret_file}"
        )
    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_file), SCOPES)
    # prompt=consent is what guarantees Google returns a reusable refresh token
    credentials = flow.run_local_server(
        port=0, access_type="offline", prompt="consent"
    )
    save_credentials(credentials, Path(settings.token_file))
    return credentials


def _refresh(credentials: Credentials) -> None:
    try:
        credentials.refresh(Request())
    except Exception as error:
        raise GmailAuthUnavailable(
            "Gmail OAuth refresh failed. The refresh token is likely revoked or "
            "expired; re-run scripts/gmail_bootstrap.py to mint a new one."
        ) from error


def save_credentials(credentials: Credentials, token_file: Path) -> None:
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(credentials.to_json(), encoding="utf-8")
