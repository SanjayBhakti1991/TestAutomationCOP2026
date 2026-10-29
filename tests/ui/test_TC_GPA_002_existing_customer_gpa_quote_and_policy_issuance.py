import json
import re
from os import getenv
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.quote_page import QuotePage
from utils.gmail_otp import GmailOtpReader


DATA_DIR = Path(__file__).parents[2] / "data"
LOGIN_DATA = json.loads((DATA_DIR / "login_data.json").read_text(encoding="utf-8"))
QUOTE_DATA = json.loads(
    (DATA_DIR / "tc_gpa_002_quote_data.json").read_text(encoding="utf-8")
)


def required_setting(name: str) -> str:
    value = getenv(name)
    if not value:
        pytest.skip(f"Set {name} in .env before running the broker portal tests")
    return value


def equals_ignoring_case(value: str) -> re.Pattern[str]:
    return re.compile(rf"^{re.escape(value)}$", re.IGNORECASE)


def test_gpa_quote_and_policy_issuance_for_existing_customer(
    page: Page,
    gmail_otp: GmailOtpReader,
    target_base_url: str,
    tmp_path: Path,
) -> None:
    base_url = target_base_url or LOGIN_DATA["base_url"]
    customer = QUOTE_DATA["customer"]
    risk = QUOTE_DATA["risk"]

    # Step 1: log in to the Broker Portal
    login_page = LoginPage(page, base_url)
    login_page.load()
    watermark = gmail_otp.now_watermark()
    login_page.login(
        required_setting("E2E_EMAIL"),
        required_setting("E2E_PASSWORD"),
        region=LOGIN_DATA["market_region"],
        access_level=LOGIN_DATA["access_level"],
    )
    expect(login_page.verification_code_input).to_be_visible(timeout=30_000)
    login_page.verify_and_sign_in(
        gmail_otp.wait_for_code(
            LOGIN_DATA["verification_subject"], after_epoch=watermark
        )
    )
    dashboard_url = re.compile(rf"{re.escape(base_url)}/dashboard\b")
    page.wait_for_url(dashboard_url, timeout=30_000)

    dashboard_page = DashboardPage(page)
    expect(dashboard_page.heading).to_be_visible()

    # Step 2: create a new quote for Group Personal Accident
    quote_page = QuotePage(page)
    dashboard_page.start_new_quote()
    expect(quote_page.heading).to_be_visible(timeout=30_000)
    quote_page.select_product(QUOTE_DATA["product"])
    expect(quote_page.next_step_button).to_be_enabled()
    quote_page.go_to_next_step()
    expect(quote_page.company_information_heading).to_be_visible()

    # Step 3: search for and select the existing customer, then verify the details
    quote_page.select_existing_customer(customer["name"])
    expect(quote_page.saved_entity_name_input).to_have_value(
        equals_ignoring_case(customer["name"]), timeout=30_000
    )
    expect(quote_page.street_address_input).to_have_value(
        equals_ignoring_case(customer["street_address"])
    )
    expect(quote_page.city_input).to_have_value(equals_ignoring_case(customer["city"]))
    expect(quote_page.customer_postal_code_input).to_have_value(
        equals_ignoring_case(customer["postal_code"])
    )
    expect(quote_page.customer_country_input).to_have_value(
        equals_ignoring_case(customer["country"])
    )
    expect(quote_page.email_input).to_have_value(equals_ignoring_case(customer["email"]))
    expect(quote_page.contact_person_input).to_have_value(
        equals_ignoring_case(customer["contact_person"])
    )
    expect(quote_page.contact_number_input).to_have_value(customer["contact_number"])

    quote_page.edit_customer_details()
    quote_page.save_customer_changes()
    expect(quote_page.edit_customer_details_button).to_be_visible()

    quote_page.go_to_next_step()
    expect(quote_page.important_notice_heading).to_be_visible()
    quote_page.accept_important_notice()

    # Step 4: enter the risk and coverage details
    expect(quote_page.insured_persons_heading).to_be_visible()
    quote_page.fill_activities_description(risk["activities_description"])
    quote_page.add_insured_class(risk["insured_class"])
    quote_page.fill_contract_details(
        headcount=risk["headcount"],
        operative_time=risk["operative_time"],
        total_annual_wages=risk["total_annual_wages"],
        average_salary=risk["average_salary"],
        business_type=risk["business_type"],
    )
    # the portal echoes the customer's country with its own casing
    expect(quote_page.risk_country_input).to_have_value(
        equals_ignoring_case(risk["country"])
    )
    expect(quote_page.total_headcount_value).to_have_text(risk["headcount"])
    quote_page.select_optional_coverage(risk["optional_coverage"])
    expect(
        quote_page.coverage_benefit_cell(risk["optional_coverage_benefit"])
    ).to_be_visible()
    quote_page.select_claims_history_answer("No")

    # Step 5: review the quote and send it to the customer
    quote_page.open_review_quote()
    expect(quote_page.endorsement_text_heading).to_be_visible()
    quote_page.submit_endorsement_text()
    expect(quote_page.quotation_number_banner).to_be_visible(timeout=60_000)
    quotation_number = quote_page.quotation_number()
    assert quotation_number, "Review step did not display a quotation number"
    expect(quote_page.total_premium_value).not_to_be_empty()
    expect(
        quote_page.coverage_benefit_cell(risk["optional_coverage_benefit"])
    ).to_be_visible()
    quote_page.send_quotation_to_customer()
    expect(quote_page.resend_quotation_button).to_be_visible(timeout=30_000)

    # Step 6: download the quotation documents
    for document in QUOTE_DATA["quote_documents"]:
        download = quote_page.download_quote_document(document)
        saved = tmp_path / download.suggested_filename
        download.save_as(saved)
        assert saved.stat().st_size > 0, f"{document} downloaded as an empty file"
        assert quotation_number in download.suggested_filename

    # Step 7: issue the policy
    quote_page.bind_policy()
    expect(quote_page.endorsement_text_heading).to_be_visible()
    quote_page.submit_endorsement_text()

    # Step 8: verify the issued policy details
    expect(quote_page.policy_authorized_heading).to_be_visible(timeout=60_000)
    expect(quote_page.policy_issued_status).to_be_visible()
    expect(quote_page.confirmed_quotation_number_value).to_have_text(quotation_number)
    expect(quote_page.policy_number_value).to_have_text(re.compile(r"[A-Z]{2,}\d+"))
    expect(quote_page.premium_amount_value).not_to_be_empty()
    policy_number = quote_page.policy_number_value.inner_text().strip()

    # Step 9: download the policy documents
    for document in QUOTE_DATA["policy_documents"]:
        download = quote_page.download_policy_document(document)
        saved = tmp_path / download.suggested_filename
        download.save_as(saved)
        assert saved.stat().st_size > 0, f"{document} downloaded as an empty file"
        assert policy_number in download.suggested_filename
