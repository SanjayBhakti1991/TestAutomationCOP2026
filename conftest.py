import pytest

from config.settings import get_target_base_url, is_ci
from utils.gmail_auth import GmailAuthUnavailable
from utils.gmail_otp import GmailOtpReader


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--headless",
        action="store_true",
        help="Run the browser without a visible window.",
    )


def pytest_configure(config: pytest.Config) -> None:
    if config.getoption("--headless"):
        config.option.headed = False


@pytest.fixture(scope="session")
def browser_type_launch_args(pytestconfig: pytest.Config) -> dict:
    return {
        "args": ["--start-maximized"],
        "headless": pytestconfig.getoption("--headless"),
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {**browser_context_args, "no_viewport": True}


@pytest.fixture(scope="session")
def target_base_url() -> str:
    return get_target_base_url()


@pytest.fixture(scope="session")
def gmail_otp() -> GmailOtpReader:
    try:
        return GmailOtpReader()
    except GmailAuthUnavailable as error:
        if is_ci():
            pytest.fail(str(error), pytrace=False)
        pytest.skip(str(error))
