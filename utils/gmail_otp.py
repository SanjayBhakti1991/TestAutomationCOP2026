"""Reads one-time passcodes straight from the Gmail API — no Gmail UI automation."""

import base64
import re
import time
from html import unescape
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config.settings import GmailSettings, get_gmail_settings
from utils.gmail_auth import GmailAuthUnavailable, resolve_credentials


GENERIC_CODE_PATTERN = r"\b(\d{6})\b"
# Gmail's `after:` index lags a little behind delivery, so widen the query and
# rely on the exact internalDate comparison to reject stale messages.
QUERY_SKEW_SECONDS = 120
_TAG_PATTERN = re.compile(r"<[^>]+>")


class OtpNotReceived(AssertionError):
    """Raised when no fresh OTP email arrives before the timeout."""


class GmailOtpReader:
    def __init__(self, settings: GmailSettings | None = None) -> None:
        self.settings = settings or get_gmail_settings()
        credentials = resolve_credentials(self.settings)
        self.service = build(
            "gmail", "v1", credentials=credentials, cache_discovery=False
        )

    def now_watermark(self) -> int:
        """Epoch seconds to call *before* triggering the OTP send."""
        return int(time.time())

    def wait_for_code(
        self,
        subject: str,
        after_epoch: int,
        timeout: float | None = None,
        interval: float | None = None,
        pattern: str | None = None,
    ) -> str:
        timeout = timeout if timeout is not None else self.settings.otp_timeout_seconds
        interval = (
            interval if interval is not None else self.settings.otp_poll_interval_seconds
        )
        patterns = [pattern] if pattern else [self.settings.otp_regex, GENERIC_CODE_PATTERN]

        deadline = time.monotonic() + timeout
        seen_subjects: list[str] = []
        matched = 0
        backoff = interval

        while True:
            try:
                messages = self._list_fresh_messages(subject, after_epoch)
                backoff = interval
            except HttpError as error:
                status = error.resp.status
                if status in (401, 403):
                    raise GmailAuthUnavailable(
                        f"Gmail API rejected the credential: {error}"
                    ) from error
                if status not in (429, 500, 502, 503, 504):
                    raise
                messages = []
                backoff = min(backoff * 2, 30.0)

            matched = max(matched, len(messages))
            for message in messages:
                seen_subjects.append(_header(message, "Subject"))
                code = _find_code(_message_text(message.get("payload", {})), patterns)
                if code:
                    return code

            if time.monotonic() >= deadline:
                break
            time.sleep(min(backoff, max(deadline - time.monotonic(), 0.0)))

        raise OtpNotReceived(
            f"No OTP matching {patterns!r} arrived within {timeout:.0f}s for "
            f"subject {subject!r} newer than epoch {after_epoch}. "
            f"Messages matched by the query: {matched}. "
            f"Subjects seen: {sorted(set(seen_subjects)) or 'none'}."
        )

    def _list_fresh_messages(self, subject: str, after_epoch: int) -> list[dict[str, Any]]:
        query = f'subject:"{subject}" after:{after_epoch - QUERY_SKEW_SECONDS}'
        response = (
            self.service.users()
            .messages()
            .list(userId="me", q=query, maxResults=10)
            .execute()
        )
        fresh = []
        for stub in response.get("messages", []):
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=stub["id"], format="full")
                .execute()
            )
            if int(message.get("internalDate", 0)) >= after_epoch * 1000:
                fresh.append(message)
        fresh.sort(key=lambda message: int(message.get("internalDate", 0)), reverse=True)
        return fresh


def _header(message: dict[str, Any], name: str) -> str:
    headers = message.get("payload", {}).get("headers", [])
    return next(
        (h.get("value", "") for h in headers if h.get("name", "").lower() == name.lower()),
        "",
    )


def _find_code(body: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        matches = re.findall(pattern, body)
        if matches:
            return matches[-1]
    return None


def _message_text(payload: dict[str, Any]) -> str:
    plain = _collect(payload, "text/plain")
    if plain.strip():
        return plain
    return _strip_html(_collect(payload, "text/html"))


def _collect(part: dict[str, Any], mime_type: str) -> str:
    if part.get("mimeType") == mime_type:
        return _decode(part.get("body", {}).get("data"))
    return "\n".join(_collect(child, mime_type) for child in part.get("parts", []))


def _decode(data: str | None) -> str:
    if not data:
        return ""
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded).decode("utf-8", errors="replace")


def _strip_html(html: str) -> str:
    return unescape(_TAG_PATTERN.sub(" ", html))


def create_gmail_otp_reader() -> GmailOtpReader:
    return GmailOtpReader()
