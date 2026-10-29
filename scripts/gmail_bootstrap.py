"""One-time local OAuth consent that mints a reusable Gmail refresh token.

Run once, then paste the printed values into your .env (local) or CI secrets.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from config.settings import get_gmail_settings  # noqa: E402
from utils.gmail_auth import (  # noqa: E402
    GmailAuthUnavailable,
    run_interactive_consent,
)


def main() -> int:
    settings = get_gmail_settings()
    try:
        credentials = run_interactive_consent(settings)
    except GmailAuthUnavailable as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if not credentials.refresh_token:
        print(
            "ERROR: Google returned no refresh token. Revoke this app at "
            "https://myaccount.google.com/permissions and run again.",
            file=sys.stderr,
        )
        return 1

    print(f"Token cached at: {settings.token_file}")
    print("\nAdd these to CI secrets (treat the refresh token as a password):\n")
    print(f"GMAIL_CLIENT_ID={credentials.client_id}")
    print(f"GMAIL_CLIENT_SECRET={credentials.client_secret}")
    print(f"GMAIL_REFRESH_TOKEN={credentials.refresh_token}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
