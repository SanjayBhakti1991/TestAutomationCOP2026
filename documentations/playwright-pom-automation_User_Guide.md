# Playwright Test Script Generator POM Automation Agent Guide

This guide explains how to use the repository's primary custom agent:

`playwright-pom-automation`

Agent file:

`PlaywrightPOMAutomation.agent.md`

## Purpose

Use this agent to:

- Convert manual test cases into Playwright Python tests.
- Reuse and extend existing Page Objects.
- Verify unknown UI behavior with Playwright MCP.
- Investigate failed Playwright tests.
- Review tests for Page Object Model violations.
- Keep credentials, OTP values, and other secrets protected.

The agent follows this workflow:

```text
UNDERSTAND -> INSPECT -> REUSE -> VERIFY -> IMPLEMENT -> EXECUTE -> INVESTIGATE -> FIX
```

## Activate the Agent

1. Open Copilot Chat in VS Code.
2. Select `playwright-TestScript-Generator-pom` in the agent selector.
3. Provide the test case or framework task.
4. Allow the agent to inspect the repository before editing.
5. Review the execution result and validation report.

Use this agent as the primary Playwright automation agent. The other Playwright
agent files are reference agents and should not be selected for the same task
unless a different workflow is explicitly required.

## Test Case Prompt Template

Use this structure for a new test:

```text
Create Playwright Python automation for this test case.

Test Case ID: <id>
Title: <title>

Objective:
<what the test proves>

Preconditions:
- <precondition>
- <precondition>

Steps:
1. <step>
2. <step>
3. <step>

Expected results:
- <expected result>
- <expected result>

Test data:
- Reuse existing repository data where applicable.
- Credentials must come from the existing secure configuration.

Before editing, inspect the repository and identify reusable Page Objects,
methods, fixtures, utilities, and test data. Use Playwright MCP for any UI
behavior or locator that is not already verified. Execute the focused test after
implementation.
```

## Example: Broker Login with OTP

```text
Create Playwright Python automation for this test case.

Test Case ID: TC-001
Title: Broker logs in with valid credentials and Gmail OTP

Preconditions:
- A valid broker account exists.
- Gmail OTP authentication is configured locally.

Steps:
1. Open the broker login page.
2. Select the required region.
3. Select the access level.
4. Enter the broker credentials.
5. Submit the login form.
6. Read the verification code from Gmail.
7. Enter the verification code and sign in.

Expected results:
- The verification-code field becomes visible after credentials are submitted.
- The broker reaches the verified dashboard state.

Test data:
- Reuse the existing login data.
- Read credentials from the existing environment configuration.
- Never include passwords, OTP values, or tokens in this prompt.

Use the existing LoginPage and GmailOtpReader where applicable. Preserve the
OTP watermark sequence. Verify any unknown UI behavior with Playwright MCP and
execute the focused test.
```

The example is specific to the existing OTP flow. Do not copy its page names,
selectors, or expected results to an unrelated feature.

## Framework Tasks

### Create a Page Object

```text
Create or extend the Page Object required for this test case.

First inspect the repository for an existing Page Object, locator, and action
method. Follow the current constructor and inheritance patterns. Use Playwright
MCP to verify any new locator. Keep assertions in the test unless the existing
framework uses another established convention. Execute a focused validation.
```

### Add a reusable action

```text
Add the reusable Page Object action needed for this business step.

Search for an existing equivalent method first. Preserve all existing callers.
Do not create duplicate login, search, submit, or navigation methods. Verify
unknown UI behavior with Playwright MCP and run the affected test.
```

### Add test data

```text
Add only the test data required for this test case.

Inspect the repository's existing data-loading convention first. Reuse existing
values where appropriate. Do not add credentials, OTP values, tokens, or client
secrets. Do not create a new data file unless the repository convention or test
isolation requirement justifies it.
```

## Review Mode

Use this prompt for a review:

```text
Review tests/ui for Playwright Page Object Model issues.

Check for:
- raw UI interactions in tests
- unreliable or duplicated locators
- duplicated Page Object methods
- incorrect fixture usage
- arbitrary waits
- weak or missing assertions
- secret exposure
- test-data coupling
- incorrect navigation assumptions

Report findings first by severity with file references. Do not edit files.
```

Severity order:

```text
Blocker -> Major -> Minor -> Nit
```

## Debug Mode

Use this prompt for a failing test:

```text
Investigate this Playwright test failure.

Test file: <path>
Command: <command>
Failure:
<paste the failure output without secrets>

Inspect the owning Page Object, fixture, test data, and configuration. Use
Playwright MCP for UI-related failures. Identify the root cause before editing,
make the smallest fix, and rerun the same focused test. Do not weaken the
assertion.
```

The agent should classify the failure as one or more of:

- locator
- Page Object
- fixture
- test flow
- test data
- authentication
- timing
- configuration
- environment
- external dependency
- application defect

## Playwright MCP Expectations

The agent should use Playwright MCP when it needs to verify:

- an unknown page or screen
- an unknown locator
- an element role, name, label, or placeholder
- element uniqueness or interactability
- navigation behavior
- resulting application state
- a UI-related test failure

MCP is not a substitute for repository inspection. Existing verified Page
Objects and locators should be reused first.

If the application cannot be reached or MCP cannot verify the required state,
the correct result is `BLOCKED`, not a guessed selector or invented behavior.

## Repository Safety Rules

Never place the following in prompts, source files, data files, logs, or reports:

- passwords
- access tokens
- refresh tokens
- OTP values
- cookies
- client secrets
- secret JSON contents

The repository currently uses:

- `conftest.py` for browser and service fixtures
- `pages/base_page.py` for the base Page Object
- `pages/login_page.py` for the login flow
- `tests/ui/` for UI tests
- `data/login_data.json` for existing non-secret login data
- `utils/gmail_otp.py` for Gmail OTP handling
- `config/settings.py` for environment-backed Gmail settings

The agent must rediscover the current repository before implementing changes.
This list is a guide, not permission to assume that future files or folders
exist.

## Validation and Results

The agent must determine the repository's actual test command. A focused local
command currently follows this pattern:

```text
python -m pytest tests/ui/<test_file>.py --headed
```

The exact command may differ for a new test and must be confirmed from the
repository configuration.

The final report should state:

- files created
- files modified
- components reused
- application behavior verified through MCP
- exact execution command
- PASS, FAIL, or BLOCKED result
- validation performed
- remaining issues or findings

Never report `PASS` based only on code inspection.
