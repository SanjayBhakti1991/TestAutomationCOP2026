import json
import re
from os import getenv
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from utils.gmail_otp import GmailOtpReader


LOGIN_DATA = json.loads(
    (Path(__file__).parents[2] / "data" / "login_data.json").read_text(
        encoding="utf-8"
    )
)


def required_setting(name: str) -> str:
    value = getenv(name)
    if not value:
        pytest.skip(f"Set {name} in .env before running the broker login test")
    return value


def test_broker_portal_login_with_gmail_otp(
    page: Page,
    gmail_otp: GmailOtpReader,
    target_base_url: str,
    request: pytest.FixtureRequest,
) -> None:
    login_base_url = target_base_url or LOGIN_DATA["base_url"]
    email = required_setting("E2E_EMAIL")
    password = required_setting("E2E_PASSWORD")
    login_page = LoginPage(page, login_base_url)
    login_page.load()

    # take the watermark before submitting so a previous run's OTP can't match
    watermark = gmail_otp.now_watermark()
    login_page.login(
        email,
        password,
        region=LOGIN_DATA["market_region"],
        access_level=LOGIN_DATA["access_level"],
    )
    expect(login_page.verification_code_input).to_be_visible(timeout=30_000)

    verification_code = gmail_otp.wait_for_code(
        LOGIN_DATA["verification_subject"], after_epoch=watermark
    )

    login_page.verify_and_sign_in(verification_code)
    dashboard_url = re.compile(rf"{re.escape(login_base_url)}/dashboard\b")
    page.wait_for_url(dashboard_url, timeout=30_000)
    expect(page).to_have_url(dashboard_url)

    if request.config.getoption("--headed"):
        #page.pause()
        page.wait_for_timeout(10_000)
