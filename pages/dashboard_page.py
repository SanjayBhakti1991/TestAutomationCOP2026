from playwright.sync_api import Page

from pages.base_page import BasePage


class DashboardPage(BasePage):
    PATH = "/dashboard"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.heading = page.get_by_role("heading", name="Broker Workspace")
        self.new_quote_button = page.get_by_role("button", name="New Quote")
        self.search_policy_button = page.get_by_role(
            "button", name="Search Policy / Quote"
        )

    def start_new_quote(self) -> None:
        self.new_quote_button.click()
