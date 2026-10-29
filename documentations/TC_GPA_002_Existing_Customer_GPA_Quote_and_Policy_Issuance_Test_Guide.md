# TC-GPA-002: Existing Customer GPA Quote and Policy Issuance

## Test Case Information

| Field | Details |
| --- | --- |
| Test Case ID | TC-GPA-002 |
| Title | Create a GPA quote and issue a policy for an existing customer |
| Application | Broker Portal |
| Product | Group Personal Accident |
| Test Type | End-to-end UI test |
| Automation | `tests/ui/test_TC_GPA_002_existing_customer_gpa_quote_and_policy_issuance.py` |

## Objective

Verify that a broker can log in to the Broker Portal, select an existing
customer, verify and update the customer's details, create and review a Group
Personal Accident quotation, send the quotation, download quotation documents,
issue a policy, and download the policy documents.

## Preconditions

1. The Broker Portal is available at the configured target URL.
2. A valid broker account is available.
3. The following environment variables are configured:

   ```text
   E2E_EMAIL
   E2E_PASSWORD
   ```

4. Gmail OTP automation is configured. See
   [Gmail OTP Automation Setup](gmail-otp-automation-setup.md).
5. The customer `Google Ireland Limited` already exists in the Broker Portal.
6. The broker account can search for and update the existing customer.
7. The broker account has permission to create quotations and issue policies.
8. Playwright browser dependencies are installed.
9. The test data file is available at:

   ```text
   data/tc_gpa_002_quote_data.json
   ```

## Test Data

### Existing Customer

| Field | Expected Value |
| --- | --- |
| Organization | Google Ireland Limited |
| Street address | Gordon Borrow Street |
| City | Dublin |
| Postal code | D02 X288 |
| Country | Ireland |
| Email | test@gmail.com |
| Contact person | TEST QA |
| Contact number | 123456789 |

The automation searches for the exact customer name and verifies the displayed
details before saving the customer changes.

### Risk Details

| Field | Value |
| --- | --- |
| Activities description | Test Activities Test Case 2 |
| Insured class | Contractors |
| Headcount | 10 |
| Operative time | Occupational including Commuting |
| Total annual wages | 720000 |
| Average salary | 60000 |
| Country | Ireland |
| Business type | Abseiling Contractors |
| Optional coverage | Temporary Total Disablement |
| Coverage benefit | Temporary Total Disablement (TTD) - weekly benefit amount |

### Documents

Quotation documents:

- `QUOTE_SCHEDULE`
- `IPID`
- `POLICY_WORDING`

Policy documents:

- `POLICY SCHEDULE`
- `POLICY WORDING`

## Test Steps and Expected Results

### 1. Log in to the Broker Portal

1. Open the Broker Portal login page.
2. Select the configured market region.
3. Select the `Broker Portal` access level.
4. Enter the broker email and password.
5. Submit the login form.
6. Wait for the verification-code field.
7. Retrieve the new OTP from Gmail.
8. Enter the OTP and select **Verify & Sign In**.

Expected result:

- The broker reaches the dashboard.
- The dashboard heading is visible.

### 2. Start a New GPA Quote

1. Select the option to start a new quote.
2. Verify that the New Quotation page is displayed.
3. Select `Group Personal Accident`.
4. Continue to the next step.

Expected result:

- The Company Information section is displayed.
- The Next button is enabled after the product is selected.

### 3. Select and Verify the Existing Customer

1. Search for `Google Ireland Limited`.
2. Select the matching existing customer.
3. Verify the displayed organization name.
4. Verify the street address, city, postal code, country, email, contact
   person, and contact number.
5. Select **Edit Details**.
6. Save the customer changes.

Expected result:

- The correct existing customer is selected.
- All displayed customer fields match the expected test data, ignoring letter
  casing where appropriate.
- The customer changes are saved successfully.
- The **Edit Details** control remains available after saving.

### 4. Accept the Important Notice

1. Continue to the next step.
2. Review the important notice.
3. Accept the important notice.

Expected result:

- The Insured Persons section is displayed.
- The workflow allows the broker to enter risk details.

### 5. Enter Insured Person and Risk Details

1. Enter the activities description.
2. Add the `Contractors` insured class.
3. Enter the headcount, operative time, annual wages, and average salary.
4. Select the business type.
5. Verify the country shown by the portal.
6. Verify the total headcount.
7. Select `Temporary Total Disablement` as optional coverage.
8. For `Are you aware of any Personal Accident claims being made in the past
   5 years?`, select `No`.

Expected result:

- The risk details are accepted.
- The country is displayed as `Ireland`, regardless of casing.
- The total headcount displays `10`.
- The expected Temporary Total Disablement benefit is visible.
- The claims-history question is answered `No`.
- The **Review Quote** button is enabled.

### 6. Review and Send the Quotation

1. Open the quote review.
2. Review and submit the endorsement text step.
3. Wait for the quotation number.
4. Confirm that a premium is displayed.
5. Confirm that the selected coverage benefit remains visible.
6. Send the quotation to the customer.

Expected result:

- A quotation number is displayed and is not empty.
- A premium amount is displayed.
- The quotation is sent successfully.
- The Resend Quotation control is displayed.

### 7. Download Quotation Documents

1. Download each document listed in the quotation document test data.
2. Save the files to the test run's temporary directory.

Expected result for each document:

- The file is downloaded successfully.
- The file is not empty.
- The quotation number appears in the downloaded filename.

### 8. Issue the Policy

1. Select **Bind Policy**.
2. Review and submit the endorsement text step again.
3. Wait for the policy authorization result.

Expected result:

- The policy authorization result is displayed.
- The policy status is `Policy Issued Successfully`.

### 9. Verify the Issued Policy

Verify the following values:

- The confirmed quotation number matches the quotation number from the review
  step.
- A policy number is displayed.
- The policy number has the expected alphanumeric format.
- A premium amount is displayed.

### 10. Download Policy Documents

1. Download each document listed in the policy document test data.
2. Save the files to the test run's temporary directory.

Expected result for each document:

- The file is downloaded successfully.
- The file is not empty.
- The policy number appears in the downloaded filename.

## Overall Expected Result

The test passes when the existing customer is selected and verified, the GPA
risk details are entered, a quotation is created and sent, the quotation
documents are downloaded, a policy is issued from the quotation, and the policy
documents are downloaded with the correct quotation and policy identifiers in
their filenames.

## Automation Mapping

| Test Area | Repository Component |
| --- | --- |
| Broker login | `pages/login_page.py` |
| Gmail OTP retrieval | `utils/gmail_otp.py` |
| Dashboard navigation | `pages/dashboard_page.py` |
| Existing customer search and update | `pages/quote_page.py` |
| Quote and policy workflow | `pages/quote_page.py` |
| Browser and Gmail fixtures | `conftest.py` |
| Quote data | `data/tc_gpa_002_quote_data.json` |
| Login data | `data/login_data.json` |

## Execution

Run the focused test from the project root:

```powershell
python -m pytest tests/ui/test_TC_GPA_002_existing_customer_gpa_quote_and_policy_issuance.py --headed
```

The test requires access to the live Broker Portal, valid broker credentials,
Gmail OTP access, an existing `Google Ireland Limited` customer, and permission
to create and issue live test records.

## Security Notes

Do not add the following to this guide, test data, or source code:

- Real passwords
- Gmail refresh tokens
- OAuth client secrets
- OTP values
- Private customer information