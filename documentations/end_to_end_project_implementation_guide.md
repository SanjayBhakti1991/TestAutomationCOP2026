# Broker Portal Playwright Automation
# End-to-End Project Implementation Guide

## 1. Purpose and Scope

This project is a Python-based end-to-end UI automation framework for the
Broker Portal. It uses Playwright for browser automation and pytest for test
execution.

The current implementation covers:

- Broker Portal login with email, password, region, and access level.
- Gmail API-based one-time passcode (OTP) retrieval.
- Dashboard navigation.
- New Group Personal Accident (GPA) quotation creation.
- New customer creation.
- Existing customer search, verification, and update.
- Quotation review and customer delivery.
- Quotation document downloads.
- Policy binding and issuance.
- Policy document downloads.

The implementation is designed for live integration testing. It requires a
reachable Broker Portal environment, a valid broker account, and access to the
mailbox that receives login OTP messages.

## 2. Technology Stack

| Area | Technology |
| --- | --- |
| Language | Python |
| Test runner | pytest |
| Browser automation | Playwright Python |
| Browser | Chromium by default |
| UI pattern | Page Object Model (POM) |
| Authentication | Portal credentials plus Gmail OTP |
| OTP integration | Gmail API read-only scope |
| Configuration | `.env` values and JSON test data |
| CI support | GitHub Actions-compatible repository workflow |

Pinned and range-constrained dependencies are defined in
[`requirements.txt`](../requirements.txt).

## 3. Repository Structure

```text
TestAutomationCOP2026/
|-- config/
|   |-- __init__.py
|   `-- settings.py
|-- data/
|   |-- __init__.py
|   |-- login_data.json
|   |-- tc_gpa_001_quote_data.json
|   `-- tc_gpa_002_quote_data.json
|-- documentations/
|   |-- end_to_end_project_implementation_guide.md
|   |-- gmail-otp-automation-setup.md
|   |-- playwright-pom-automation_User_Guide.md
|   `-- test-case guides
|-- pages/
|   |-- base_page.py
|   |-- dashboard_page.py
|   |-- login_page.py
|   `-- quote_page.py
|-- scripts/
|   `-- gmail_bootstrap.py
|-- tests/
|   `-- ui/
|       |-- test_broker_portal_login.py
|       |-- test_TC_GPA_001_new_customer_gpa_quote_and_policy_issuance.py
|       `-- test_TC_GPA_002_existing_customer_gpa_quote_and_policy_issuance.py
|-- utils/
|   |-- gmail_auth.py
|   `-- gmail_otp.py
|-- conftest.py
|-- pytest.ini
`-- requirements.txt
```

Generated or sensitive artifacts are intentionally excluded from source
control through [`.gitignore`](../.gitignore), including `.env`, Gmail OAuth
files, test results, and browser caches.

## 4. Architecture and Responsibilities

### 4.1 Test layer

The UI tests express business flows and assertions. They load JSON data,
obtain credentials from environment variables, call page-object actions, and
verify business outcomes.

- [`test_broker_portal_login.py`](../tests/ui/test_broker_portal_login.py)
  validates login and OTP verification.
- [`test_TC_GPA_001_new_customer_gpa_quote_and_policy_issuance.py`](../tests/ui/test_TC_GPA_001_new_customer_gpa_quote_and_policy_issuance.py)
  creates a new customer, creates a GPA quote, issues a policy, and validates
  downloaded documents.
- [`test_TC_GPA_002_existing_customer_gpa_quote_and_policy_issuance.py`](../tests/ui/test_TC_GPA_002_existing_customer_gpa_quote_and_policy_issuance.py)
  selects and updates an existing customer before running the same quotation
  and policy flow.

Assertions remain in the test layer so the business outcome is visible in the
test itself.

### 4.2 Page Object layer

All reusable UI locators and user actions are encapsulated in the `pages`
package:

- [`BasePage`](../pages/base_page.py) provides the common Playwright page
  reference and navigation helper.
- [`LoginPage`](../pages/login_page.py) owns region selection, access-level
  selection, credentials, OTP verification, and login controls.
- [`DashboardPage`](../pages/dashboard_page.py) owns dashboard assertions and
  the New Quote action.
- [`QuotePage`](../pages/quote_page.py) owns the multi-step quotation wizard,
  customer selection, risk details, coverage, quote review, document downloads,
  and policy issuance.

Locators use accessible roles, labels, placeholders, and exact text wherever
possible. Tests should call page-object methods instead of performing raw UI
interactions.

### 4.3 Fixture and configuration layer

[`conftest.py`](../conftest.py) provides:

- `--headless` command-line support.
- Chromium launch configuration.
- A maximized, no-viewport browser context.
- `target_base_url`, loaded from `E2E_BASE_URL`.
- A session-scoped `gmail_otp` fixture.

[`config/settings.py`](../config/settings.py) loads `.env` values and supplies
defaults for the target URL, Gmail token location, OTP extraction pattern, OTP
timeout, and polling interval.

### 4.4 Gmail authentication and OTP layer

- [`gmail_auth.py`](../utils/gmail_auth.py) resolves OAuth credentials.
- [`gmail_otp.py`](../utils/gmail_otp.py) queries Gmail and extracts a fresh
  six-digit OTP.
- [`gmail_bootstrap.py`](../scripts/gmail_bootstrap.py) performs one-time
  local OAuth consent and prints the values needed for CI configuration.

The Gmail integration uses only:

```text
https://www.googleapis.com/auth/gmail.readonly
```

It does not automate the Gmail website and cannot send, delete, or modify
messages.

## 5. End-to-End Runtime Flow

The normal business flow is:

```text
pytest
  |
  v
Playwright opens /login
  |
  v
Select region and access level
  |
  v
Submit portal credentials
  |
  v
Portal sends OTP email
  |
  v
GmailOtpReader finds a fresh message after the watermark
  |
  v
Enter OTP and navigate to /dashboard
  |
  v
Open /quotes/new
  |
  +--> New customer flow (TC-GPA-001)
  |
  `--> Existing customer flow (TC-GPA-002)
          |
          v
Enter GPA risk and coverage details
  |
  v
Review quote and obtain quotation number
  |
  v
Send quotation and download quote documents
  |
  v
Bind policy and obtain policy number
  |
  v
Download policy documents
```

### 5.1 Login and OTP sequence

The OTP watermark must be captured before the login request:

```python
watermark = gmail_otp.now_watermark()
login_page.login(email, password, region=region, access_level=access_level)
verification_code = gmail_otp.wait_for_code(subject, after_epoch=watermark)
login_page.verify_and_sign_in(verification_code)
```

This prevents a stale OTP from an earlier run from being accepted. Gmail
search uses a small indexing skew, then the message `internalDate` is checked
against the watermark for freshness.

### 5.2 New customer flow

The new-customer scenario:

1. Selects `Group Personal Accident`.
2. Opens the Add New Company form.
3. Enters company details and saves the customer.
4. Accepts the important notice.
5. Enters insured-person and risk details.
6. Selects optional coverage and answers the claims-history question.
7. Reviews and sends the quotation.
8. Downloads all configured quote documents.
9. Binds the policy and verifies the issued policy.
10. Downloads all configured policy documents.

### 5.3 Existing customer flow

The existing-customer scenario:

1. Selects `Group Personal Accident`.
2. Searches for the configured customer by exact displayed name.
3. Verifies all returned customer fields.
4. Enters edit mode and saves the customer details.
5. Continues through the same notice, risk, quote, and policy flow.

Customer values are compared case-insensitively where the portal may change
display casing.

## 6. Initial Setup

### 6.1 Prerequisites

Install the following before running the project:

- Python compatible with the installed project dependencies.
- Git, if the project is being obtained from source control.
- Access to the target Broker Portal environment.
- A broker account authorized to create quotes and issue policies.
- A Gmail mailbox that receives the broker portal OTP.
- Google Cloud access to configure Gmail API OAuth.

### 6.2 Create and activate a virtual environment

From the project root on Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell execution policy prevents activation, run the commands using the
Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 6.3 Install the Playwright browser

```powershell
python -m playwright install chromium
```

The default pytest configuration runs Chromium in headed mode. Use
`--headless` when a visible browser is not available.

### 6.4 Configure the local environment

Create a root-level `.env` file. Do not commit it.

```env
E2E_BASE_URL=https://your-broker-portal-environment.example
E2E_EMAIL=broker-user@example.com
E2E_PASSWORD=replace-with-secret

GMAIL_CLIENT_SECRET_FILE=auth/client_secret.json
GMAIL_TOKEN_FILE=auth/gmail_token.json
```

If `E2E_BASE_URL` is empty, the tests fall back to the base URL in
`data/login_data.json`. Using `E2E_BASE_URL` is recommended because it keeps
environment selection out of test code and allows the same tests to target
different environments.

Optional Gmail settings:

```env
OTP_REGEX=Verification Details:\s*(\d{6})
OTP_TIMEOUT_SECONDS=90
OTP_POLL_INTERVAL_SECONDS=3
```

## 7. Gmail OAuth Setup

Follow the more detailed
[Gmail OTP setup guide](gmail-otp-automation-setup.md) for Google Cloud
configuration. The implementation sequence is:

1. Enable the Gmail API in a Google Cloud project.
2. Configure the OAuth consent screen.
3. Add the OTP-receiving Gmail account as a test user when required.
4. Create a Desktop OAuth client.
5. Download the client secret JSON file to `auth/client_secret.json`.
6. Run:

   ```powershell
   python scripts/gmail_bootstrap.py
   ```

7. Complete the interactive consent flow.
8. Confirm that `auth/gmail_token.json` was created.

The token and client secret are sensitive. Never place their contents in
source files, test data, documentation, logs, or pull requests.

Credential resolution order is:

1. `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, and `GMAIL_REFRESH_TOKEN`.
2. The local token file configured by `GMAIL_TOKEN_FILE`.
3. Interactive OAuth consent for local execution only.

In CI, missing credentials fail the test instead of starting interactive
consent. This makes secret configuration problems visible in the pipeline.

## 8. Test Data Contract

### 8.1 Login data

[`data/login_data.json`](../data/login_data.json) contains non-secret login
parameters:

```json
{
  "base_url": "https://...",
  "market_region": "IE",
  "access_level": "Broker Portal",
  "verification_subject": "Verification Code from Aviva"
}
```

Passwords and OTP values must never be stored in this file.

### 8.2 New customer GPA data

[`data/tc_gpa_001_quote_data.json`](../data/tc_gpa_001_quote_data.json)
contains:

- Product name.
- New company details.
- Activities and insured class.
- Headcount and financial values.
- Operative time and business type.
- Optional coverage and expected benefit.
- Quote document names.
- Policy document names.

The organization name must be unique enough for the target environment to
avoid collisions between repeated runs.

### 8.3 Existing customer GPA data

[`data/tc_gpa_002_quote_data.json`](../data/tc_gpa_002_quote_data.json)
contains:

- Existing customer search name.
- Expected customer details.
- Risk and coverage values.
- Quote and policy document names.

The selected customer must already exist and the broker account must have
permission to edit it.

## 9. Running the Tests

Run all configured tests:

```powershell
python -m pytest
```

Run in headless mode:

```powershell
python -m pytest --headless
```

Run the login smoke test:

```powershell
python -m pytest tests/ui/test_broker_portal_login.py --headed
```

Run the new-customer GPA flow:

```powershell
python -m pytest tests/ui/test_TC_GPA_001_new_customer_gpa_quote_and_policy_issuance.py --headed
```

Run the existing-customer GPA flow:

```powershell
python -m pytest tests/ui/test_TC_GPA_002_existing_customer_gpa_quote_and_policy_issuance.py --headed
```

The default configuration in [`pytest.ini`](../pytest.ini) sets:

```ini
testpaths = tests
addopts = --browser chromium --headed
```

The quote and policy tests create live business records. Run them only in an
approved test environment with test data and permissions appropriate for
creating quotations and issuing policies.

## 10. Assertions and Business Outcomes

The suite verifies more than navigation:

### Authentication

- Verification-code field appears after credential submission.
- The OTP is fresh and matches the configured email subject/pattern.
- The browser reaches `/dashboard`.
- The Broker Workspace heading is visible.

### Quotation

- The New Quotation page is displayed.
- The selected product is accepted.
- Customer details are saved or retrieved correctly.
- The important notice can be accepted.
- Risk details and headcount are reflected in the UI.
- The selected benefit is visible.
- A quotation number is generated.
- A premium is displayed.
- Quotation delivery completes and Resend Quotation is visible.

### Documents

For each configured download:

- Playwright receives a download event.
- The saved file is non-empty.
- The quotation number or policy number appears in the filename.

### Policy

- Policy authorization is displayed.
- Policy status is `Policy Issued Successfully`.
- The issued quotation number matches the reviewed quotation.
- A policy number with the expected alphanumeric shape is displayed.
- A premium amount is displayed.

## 11. Failure Handling and Troubleshooting

### Missing `E2E_EMAIL` or `E2E_PASSWORD`

The test skips with a message identifying the missing environment variable.
Set both values in `.env` for local execution or as CI secrets for pipeline
execution.

### Gmail authentication unavailable

For local runs:

- Confirm `GMAIL_CLIENT_SECRET_FILE` points to an existing OAuth client file.
- Confirm the Gmail token file exists or rerun
  `python scripts/gmail_bootstrap.py`.
- Confirm the authorized Gmail account receives the portal OTP.

For CI:

- Configure `GMAIL_CLIENT_ID`.
- Configure `GMAIL_CLIENT_SECRET`.
- Configure `GMAIL_REFRESH_TOKEN`.
- Do not rely on interactive consent.

### OTP not found

Check:

- The OTP was sent to the configured mailbox.
- `verification_subject` matches the actual subject.
- The watermark was captured before login submission.
- `OTP_REGEX` matches the email body.
- The timeout is sufficient for the environment.
- Gmail API access is enabled.

The reader checks plain text first and falls back to HTML text. It also
handles temporary Gmail API rate-limit and server errors with bounded
backoff, while authentication errors are reported explicitly.

### Customer cannot be selected

Check:

- The customer exists in the target environment.
- The configured name matches the displayed suggestion exactly.
- The broker has customer-search permission.
- The existing-customer data file is aligned with the current environment.

### Address or country selection fails

The new-customer flow uses the portal's address lookup and explicitly chooses
manual entry when needed. Confirm that the address lookup response is
available and that the configured country is present in the picker.

### Download assertion fails

Check:

- The portal generated the document.
- The document label in the JSON file matches the UI exactly.
- The browser has download permission.
- The expected identifier is included in the application-generated filename.

### Browser or test timing failures

Prefer the existing Playwright assertions and URL waits over arbitrary sleeps.
The current tests use longer waits only for external operations such as OTP
delivery, quote generation, and policy issuance.

## 12. CI/CD Guidance

The repository includes
[`.github/workflows/copilot-setup-steps.yml`](../.github/workflows/copilot-setup-steps.yml).
Its current commands are oriented toward a Node project (`npm ci`, `npx
playwright install`, and `npx run build`), while this repository's executable
test stack is Python/pytest.

For a production test pipeline, the workflow should be aligned with the
actual project by:

1. Checking out the repository.
2. Setting up the supported Python version.
3. Installing `requirements.txt`.
4. Installing Chromium with `python -m playwright install --with-deps chromium`.
5. Supplying the portal and Gmail values through encrypted CI secrets.
6. Running the focused smoke test first.
7. Running the quote/policy tests only when the target environment is
   available and test-record creation is approved.
8. Publishing pytest and Playwright artifacts on failure.

Recommended CI secret names:

```text
E2E_BASE_URL
E2E_EMAIL
E2E_PASSWORD
GMAIL_CLIENT_ID
GMAIL_CLIENT_SECRET
GMAIL_REFRESH_TOKEN
```

Never echo these values in workflow logs. Treat the Gmail refresh token and
portal password as passwords.

## 13. Development and Extension Standards

When adding a new automated flow:

1. Identify the business outcome and test data contract.
2. Search the existing `pages` package before adding locators or actions.
3. Reuse `LoginPage`, `DashboardPage`, `QuotePage`, and the Gmail fixture when
   the flow uses the same screens.
4. Keep raw UI interactions in page objects.
5. Keep business assertions in tests.
6. Add non-secret data to a dedicated JSON file when the scenario requires
   isolation.
7. Use environment variables for credentials, tokens, URLs, and other
   environment-specific values.
8. Use accessible roles and stable labels rather than CSS implementation
   details.
9. Use explicit Playwright expectations for state changes.
10. Run the smallest focused test before running the full suite.

The repository's
[Playwright POM agent guide](playwright-pom-automation_User_Guide.md)
provides prompt templates and review/debugging conventions for extending the
framework.

## 14. Team Handoff Checklist

Before sharing or executing the project, confirm:

- [ ] Python environment is created and dependencies are installed.
- [ ] Chromium is installed for Playwright.
- [ ] The target portal URL is reachable.
- [ ] The broker account is authorized for the selected flows.
- [ ] `.env` exists locally but is not committed.
- [ ] Gmail API is enabled and OAuth consent is complete.
- [ ] Gmail token or CI refresh-token secrets are available.
- [ ] The OTP subject and extraction pattern are correct.
- [ ] New-customer data is safe to create repeatedly in the test environment.
- [ ] Existing-customer data points to a valid test customer.
- [ ] Quote and policy document labels match the target application.
- [ ] The login smoke test passes before running live quote/policy tests.
- [ ] Test artifacts and failures are retained for investigation.
- [ ] No passwords, tokens, client secrets, OTPs, or private mailbox data are
      included in commits or documentation.

## 15. Source of Truth

This guide describes the implementation currently present in the repository.
For changes to selectors, workflow steps, environment variables, test data, or
Gmail behavior, update the corresponding source file and then update this
guide and the relevant focused test-case guide together.
