from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class LoginPage(BasePage):
    PATH = "/login"
    REGION_NAMES = {
        "IE": "Ireland",
        "NO": "Norway",
        "SE": "Sweden",
    }

    def __init__(self, page: Page, target_base_url: str) -> None:
        super().__init__(page)
        self.target_base_url = target_base_url

        self.heading = page.get_by_role("heading", name="global Portal")
        self.access_level_select = page.get_by_role("combobox", name="Access Level")
        self.email_input = page.get_by_role("textbox", name="Email or User ID")
        # placeholder stays constant when the show/hide toggle switches the input type
        self.password_input = page.get_by_placeholder("\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022")
        self.password_toggle_button = self.password_input.locator(
            "xpath=following-sibling::button[1]"
        )
        self.login_button = page.get_by_role("button", name="Secure Login")
        self.reset_password_button = page.get_by_role("button", name="Reset here")
        self.verification_alert = page.get_by_role("alert")
        self.verification_code_input = page.get_by_role(
            "textbox", name="Enter Verification Code"
        )
        self.resend_code_button = page.get_by_role("button", name="Resend code")
        self.use_different_credentials_button = page.get_by_role(
            "button", name="Use different credentials"
        )
        self.verify_and_sign_in_button = page.get_by_role(
            "button", name="Verify & Sign In"
        )

    def load(self) -> None:
        self.navigate_to(f"{self.target_base_url}{self.PATH}")

    def region_button(self, region: str) -> Locator:
        region_name = self.REGION_NAMES.get(region.upper(), region)
        return self.page.get_by_role("button", name=f"Select {region_name} region")

    def select_region(self, region: str) -> None:
        self.region_button(region).click()

    def select_access_level(self, access_level: str) -> None:
        self.access_level_select.select_option(label=access_level)

    def fill_credentials(self, email: str, password: str) -> None:
        self.email_input.fill(email)
        self.password_input.fill(password)

    def toggle_password_visibility(self) -> None:
        self.password_toggle_button.click()

    def is_password_visible(self) -> bool:
        return self.password_input.get_attribute("type") == "text"

    def submit(self) -> None:
        self.login_button.click()

    def fill_verification_code(self, verification_code: str) -> None:
        self.verification_code_input.fill(verification_code)

    def verify_and_sign_in(self, verification_code: str) -> None:
        self.fill_verification_code(verification_code)
        self.verify_and_sign_in_button.click()

    def resend_verification_code(self) -> None:
        self.resend_code_button.click()

    def use_different_credentials(self) -> None:
        self.use_different_credentials_button.click()

    def login(
        self,
        email: str,
        password: str,
        region: str | None = None,
        access_level: str | None = None,
    ) -> None:
        if region:
            self.select_region(region)
        if access_level:
            self.select_access_level(access_level)
        self.fill_credentials(email, password)
        self.submit()
