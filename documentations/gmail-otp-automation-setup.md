# Gmail OTP Automation Setup

This project reads one-time passcodes from Gmail through the Gmail API and
enters them into the application automatically. It does not automate the
Gmail website.

## 1. Install Dependencies

From the project root, install the required packages:

```bash
pip install -r requirements.txt
```

The Gmail integration uses the Google API and OAuth packages listed in
`requirements.txt`.

## 2. Create a Google Cloud OAuth Application

1. Open the Google Cloud Console.
2. Create or select a Google Cloud project.
3. Enable the Gmail API.
4. Configure the OAuth consent screen.
5. Add the Gmail account that receives the OTP as a test user when required.
6. Create an OAuth client ID.
7. Select **Desktop app** as the application type.
8. Download the client secret JSON file.

Store the downloaded file locally as:

```text
auth/client_secret.json
```

Do not commit this file to source control.

## 3. Configure the Local Environment

Create a `.env` file in the project root:

```env
E2E_EMAIL=broker-user@example.com
E2E_PASSWORD=your-portal-password

GMAIL_CLIENT_SECRET_FILE=auth/client_secret.json
GMAIL_TOKEN_FILE=auth/gmail_token.json
```

The Gmail account used during OAuth must be the mailbox that receives the
application OTP.

Optional OTP settings are:

```env
OTP_REGEX=Verification Details:\s*(\d{6})
OTP_TIMEOUT_SECONDS=90
OTP_POLL_INTERVAL_SECONDS=3
```

The default values are defined in `config/settings.py`.

## 4. Generate the Gmail OAuth Token

Run the bootstrap script once:

```bash
python scripts/gmail_bootstrap.py
```

The script opens a browser and starts Google's OAuth consent flow:

1. Sign in with the Gmail account that receives the OTP.
2. Grant the requested Gmail read-only permission.
3. Complete the consent flow.
4. Close the browser after authorization finishes.

The reusable token is saved to:

```text
auth/gmail_token.json
```

The script also prints values that can be stored as CI secrets:

```text
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
GMAIL_REFRESH_TOKEN=...
```

Treat the refresh token like a password.

## 5. How Gmail Authentication Works

Credential resolution is implemented in `utils/gmail_auth.py`.

The authentication order is:

1. Use `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, and
   `GMAIL_REFRESH_TOKEN` when all three are configured.
2. Otherwise, load the token from `GMAIL_TOKEN_FILE`.
3. If the local token is expired, refresh it and save the updated token.
4. If no token exists locally, start interactive OAuth consent.
5. In CI, interactive consent is unavailable, so missing credentials fail the
   test.

The requested scope is:

```text
https://www.googleapis.com/auth/gmail.readonly
```

The automation can read Gmail messages but cannot send, delete, or modify
emails.

## 6. How the OTP Is Retrieved

The implementation is in `utils/gmail_otp.py`.

The process is:

1. Record the current time before submitting the login form.

   ```python
   watermark = gmail_otp.now_watermark()
   ```

2. Submit the application credentials.
3. Allow the application to send a new OTP email.
4. Search Gmail using the configured subject and a time filter.
5. Load matching messages in full.
6. Compare each message's `internalDate` with the watermark.
7. Reject OTP messages from earlier test runs.
8. Read plain-text content, falling back to HTML content when necessary.
9. Extract the OTP using `OTP_REGEX`.
10. Poll until the code arrives or the timeout is reached.

The Gmail search uses a small time skew because Gmail search indexing can lag
behind message delivery. The exact message timestamp check prevents stale
messages from being accepted.

The default email subject is configured in `data/login_data.json`:

```json
"verification_subject": "Verification Code from Aviva"
```

## 7. How the Pytest Fixture Works

The `gmail_otp` fixture is defined in `conftest.py` and creates one reader
for the test session:

```python
@pytest.fixture(scope="session")
def gmail_otp() -> GmailOtpReader:
    return GmailOtpReader()
```

Tests receive the reader through pytest dependency injection:

```python
def test_broker_portal_login_with_gmail_otp(
    page: Page,
    gmail_otp: GmailOtpReader,
    target_base_url: str,
) -> None:
```

If Gmail authentication is unavailable, local tests are skipped with an
explanatory message. CI tests fail so missing secret configuration is visible.

## 8. How the Login Test Uses the OTP

The login test in `tests/ui/test_broker_portal_login.py` follows this order:

```python
watermark = gmail_otp.now_watermark()

login_page.login(
    email,
    password,
    region=LOGIN_DATA["market_region"],
    access_level=LOGIN_DATA["access_level"],
)

expect(login_page.verification_code_input).to_be_visible(timeout=30_000)

verification_code = gmail_otp.wait_for_code(
    LOGIN_DATA["verification_subject"],
    after_epoch=watermark,
)

login_page.verify_and_sign_in(verification_code)
```

The watermark must be captured before submitting the login form. Otherwise,
the test could accidentally use an OTP from an earlier test run.

## 9. Run the Test Locally

Run the focused broker login test:

```bash
pytest tests/ui/test_broker_portal_login.py
```

The test will:

1. Open the broker portal.
2. Enter the configured credentials.
3. Trigger the OTP email.
4. Read the new OTP from Gmail.
5. Enter the OTP.
6. Verify navigation to the dashboard.

## 10. Configure CI

Do not commit `.env`, OAuth client secrets, token files, or refresh tokens.

Configure these as CI secret variables:

```text
E2E_EMAIL
E2E_PASSWORD
GMAIL_CLIENT_ID
GMAIL_CLIENT_SECRET
GMAIL_REFRESH_TOKEN
```

CI uses the refresh-token flow and does not require
`GMAIL_CLIENT_SECRET_FILE` or `GMAIL_TOKEN_FILE`.

## 11. Repeat the Setup for Another User

1. Provide the user with a valid application account.
2. Confirm which Gmail inbox receives that account's OTP.
3. Provide an approved Google OAuth client configuration.
4. Add the user's Gmail account as an OAuth test user when required.
5. Download the OAuth client secret JSON file.
6. Run `python scripts/gmail_bootstrap.py` while signed in to that Gmail
   account.
7. Store the generated token outside source control.
8. Set the user's `E2E_EMAIL` and `E2E_PASSWORD` values.
9. Confirm the OTP subject in `data/login_data.json`.
10. Confirm the OTP format matches `OTP_REGEX`.
11. Run the focused login test.

The Gmail account used for OAuth must be able to read the inbox where the
portal sends the OTP.

## 12. Troubleshooting

### No OTP is found

Check the following:

- The Gmail account is the correct inbox.
- The subject matches `verification_subject`.
- The OTP email arrived after the watermark.
- `OTP_REGEX` matches the email body.
- The timeout is long enough.
- The Gmail API is enabled.

### OAuth refresh fails

The refresh token may have been revoked or expired. Run the bootstrap script
again and update the CI secret:

```bash
python scripts/gmail_bootstrap.py
```

### CI reports missing Gmail credentials

Verify that all three Gmail CI secrets are configured:

```text
GMAIL_CLIENT_ID
GMAIL_CLIENT_SECRET
GMAIL_REFRESH_TOKEN
```

## Security Requirements

Never commit any of the following:

- `auth/client_secret.json`
- `auth/gmail_token.json`
- `.env`
- Gmail refresh tokens
- Application passwords
- OTP values