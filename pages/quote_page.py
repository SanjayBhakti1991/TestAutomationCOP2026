import re

from playwright.sync_api import Download, Locator, Page

from pages.base_page import BasePage


class QuotePage(BasePage):
    """The multi-step New Quotation wizard served from /quotes/new."""

    PATH = "/quotes/new"
    QUOTATION_NUMBER_PATTERN = re.compile(r"[A-Z]{2,}\d+")

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.heading = page.get_by_role("heading", name="New Quotation")
        self.next_step_button = page.get_by_role("button", name="Next Step")

        self.company_information_heading = page.get_by_role(
            "heading", name="Company Information"
        )
        self.add_new_company_button = page.get_by_role("button", name="Add New Company")
        self.customer_search_input = page.get_by_role(
            "textbox", name="Search Existing Customer"
        )
        self.edit_customer_details_button = page.get_by_role(
            "button", name="Edit Details"
        )
        self.save_customer_changes_button = page.get_by_role(
            "button", name="Save Changes"
        )
        self.back_to_customer_search_button = page.get_by_role(
            "button", name="Back to Search"
        )
        # the selected-customer panel labels these two fields differently from the
        # Add New Company form, which uses an Eircode label and a country picker
        self.customer_postal_code_input = page.get_by_role(
            "textbox", name="Postal Code"
        )
        self.customer_country_input = page.get_by_role("textbox", name="Country")
        self.organization_name_input = page.get_by_role(
            "textbox", name="Organization Full Name"
        )
        self.street_address_input = page.get_by_role("textbox", name="Street Address")
        self.address_enter_manually_button = page.get_by_role(
            "button", name="Enter manually"
        )
        self.city_input = page.get_by_role("textbox", name="City")
        self.postal_code_input = page.get_by_role(
            "textbox", name="Eircode / Postal Code"
        )
        self.country_picker_button = page.get_by_role("button", name="Select...")
        self.country_search_input = page.get_by_placeholder("Type to search...")
        self.email_input = page.get_by_role("textbox", name="Email", exact=False)
        self.contact_person_input = page.get_by_role("textbox", name="Contact Person")
        self.contact_number_input = page.get_by_role("textbox", name="Contact No")
        self.save_customer_button = page.get_by_role("button", name="Save Customer")
        self.saved_entity_name_input = page.get_by_role("textbox", name="Entity Name")

        self.important_notice_heading = page.get_by_role(
            "heading", name="Important", exact=True
        )
        # the notice body is the sibling scroll container; the accept button stays
        # disabled until it has been scrolled to the end
        self.important_notice_body = self.important_notice_heading.locator(
            "xpath=../following-sibling::div[1]"
        )
        self.accept_and_continue_button = page.get_by_role(
            "button", name="Accept and Continue"
        )

        self.insured_persons_heading = page.get_by_role(
            "heading", name="Insured Persons"
        )
        self.activities_description_input = page.get_by_placeholder(
            "Describe main activities"
        )
        self.insured_class_search_input = page.get_by_placeholder(
            "Search & Add Insured Class..."
        )
        self.total_headcount_value = page.get_by_text("TOTAL HEADCOUNT").locator(
            "xpath=following-sibling::p[1]"
        )
        self.headcount_input = page.get_by_role("spinbutton", name="Headcount")
        self.operative_time_select = page.get_by_role(
            "combobox", name="Operative Time"
        )
        self.total_annual_wages_input = page.get_by_role(
            "textbox", name="Total Annual Wages"
        )
        self.risk_country_input = page.get_by_role("textbox", name="Country")
        self.average_salary_input = page.get_by_role("textbox", name="Average Salary")
        self.business_type_select = page.get_by_role(
            "combobox", name="Type of Business or Organisation"
        )
        self.claims_history_question = page.get_by_text(
            re.compile(
                r"Are you aware of any Personal Accident claims being made "
                r"in the past 5 years\?"
            ),
            exact=False,
        )
        self.review_quote_button = page.get_by_role("button", name="Review Quote")

        self.endorsement_text_heading = page.get_by_role(
            "heading", name="Endorsement Text"
        )
        self.endorsement_text_input = page.get_by_placeholder(
            "Enter any endorsements, special conditions, or policy notes..."
        )
        self.endorsement_dialog = self.endorsement_text_heading.locator(
            "xpath=ancestor::div[2]"
        )
        self.endorsement_next_button = self.endorsement_dialog.get_by_role(
            "button", name="Next", exact=True
        )

        self.quotation_number_banner = page.locator("p").filter(
            has_text=re.compile(r"Quotation No\s*:")
        ).first
        self.total_premium_value = page.get_by_text("Total Premium").locator(
            "xpath=following-sibling::div[1]"
        )
        self.send_quotation_button = page.get_by_role("button", name="Yes, Send")
        self.hold_quotation_button = page.get_by_role("button", name="No, Hold")
        self.resend_quotation_button = page.get_by_role(
            "button", name="Resend Quotation"
        )
        self.confirm_delivery_heading = page.get_by_role(
            "heading", name="Confirm Quotation Delivery"
        )
        self.confirm_delivery_dialog = self.confirm_delivery_heading.locator(
            "xpath=ancestor::div[1]"
        )
        self.confirm_delivery_button = self.confirm_delivery_dialog.get_by_role(
            "button", name="Confirm", exact=True
        )
        self.bind_policy_button = page.get_by_role("button", name="Bind Policy")

        self.policy_authorized_heading = page.get_by_role(
            "heading", name="Policy Authorized"
        )
        self.policy_issued_status = page.get_by_text("Policy Issued Successfully")
        self.policy_number_value = self._confirmation_value("Policy Number")
        self.confirmed_quotation_number_value = self._confirmation_value(
            "Quotation Number"
        )
        self.premium_amount_value = self._confirmation_value("Premium Amount")

    def _confirmation_value(self, label: str) -> Locator:
        return self.page.get_by_text(label, exact=True).locator(
            "xpath=following-sibling::span[1]"
        )

    def product_card(self, product: str) -> Locator:
        return self.page.get_by_role("button").filter(
            has=self.page.get_by_role("heading", name=product, exact=True)
        )

    def select_product(self, product: str) -> None:
        self.product_card(product).click()

    def go_to_next_step(self) -> None:
        self.next_step_button.click()

    def open_new_company_form(self) -> None:
        self.add_new_company_button.click()

    def customer_suggestion(self, customer_name: str) -> Locator:
        # several customers share a name prefix, so match the suggestion label exactly
        return (
            self.page.get_by_role("button")
            .filter(has=self.page.get_by_text(customer_name, exact=True))
            .first
        )

    def select_existing_customer(self, customer_name: str) -> None:
        self.customer_search_input.press_sequentially(customer_name)
        self.customer_suggestion(customer_name).click()

    def edit_customer_details(self) -> None:
        self.edit_customer_details_button.click()

    def save_customer_changes(self) -> None:
        self.save_customer_changes_button.click()

    def _enter_street_address(self, street_address: str) -> None:
        # the field is an address lookup; manual entry is offered when nothing matches
        self.street_address_input.press_sequentially(street_address)
        self.address_enter_manually_button.click()

    def select_country(self, country: str) -> None:
        self.country_picker_button.click()
        self.page.get_by_role("listitem").filter(
            has_text=re.compile(rf"^{re.escape(country)}$", re.IGNORECASE)
        ).click()

    def fill_company_details(
        self,
        organization_name: str,
        street_address: str,
        city: str,
        postal_code: str,
        country: str,
        email: str,
        contact_person: str,
        contact_number: str,
    ) -> None:
        self.organization_name_input.fill(organization_name)
        self._enter_street_address(street_address)
        self.city_input.fill(city)
        self.postal_code_input.fill(postal_code)
        self.select_country(country)
        self.email_input.fill(email)
        self.contact_person_input.fill(contact_person)
        self.contact_number_input.fill(contact_number)

    def save_customer(self) -> None:
        self.save_customer_button.click()

    def accept_important_notice(self) -> None:
        self.important_notice_body.evaluate("el => el.scrollTo(0, el.scrollHeight)")
        self.accept_and_continue_button.click()

    def fill_activities_description(self, description: str) -> None:
        self.activities_description_input.fill(description)

    def insured_class_suggestion(self, insured_class: str) -> Locator:
        # the suggestion panel is a sibling of the search input's wrapper, not of the input
        return (
            self.insured_class_search_input.locator("xpath=ancestor::div[3]")
            .get_by_role("button")
            .filter(has_text=insured_class)
        )

    def add_insured_class(self, insured_class: str) -> None:
        self.insured_class_search_input.press_sequentially(insured_class)
        self.insured_class_suggestion(insured_class).click()

    def fill_contract_details(
        self,
        headcount: str,
        operative_time: str,
        total_annual_wages: str,
        average_salary: str,
        business_type: str,
    ) -> None:
        self.headcount_input.fill(headcount)
        self.operative_time_select.select_option(label=operative_time)
        self.total_annual_wages_input.fill(total_annual_wages)
        self.average_salary_input.fill(average_salary)
        self.business_type_select.select_option(label=business_type)

    def coverage_card_heading(self, coverage: str) -> Locator:
        return self.page.get_by_role("heading", name=coverage, exact=True)

    def coverage_benefit_cell(self, benefit: str) -> Locator:
        return self.page.get_by_role("cell", name=benefit, exact=True)

    def select_optional_coverage(self, coverage: str) -> None:
        self.coverage_card_heading(coverage).click()

    def select_claims_history_answer(self, answer: str) -> None:
        normalized_answer = answer.strip().casefold()
        if normalized_answer not in {"yes", "no"}:
            raise ValueError("Claims history answer must be 'Yes' or 'No'")

        self.claims_history_question.first.locator("xpath=..").get_by_role(
            "checkbox", name=normalized_answer.title(), exact=True
        ).check()

    def open_review_quote(self) -> None:
        self.review_quote_button.click()

    def submit_endorsement_text(self, endorsement_text: str = "") -> None:
        if endorsement_text:
            self.endorsement_text_input.fill(endorsement_text)
        self.endorsement_next_button.click()

    def quotation_number(self) -> str:
        match = self.QUOTATION_NUMBER_PATTERN.search(
            self.quotation_number_banner.inner_text()
        )
        return match.group() if match else ""

    def send_quotation_to_customer(self) -> None:
        self.send_quotation_button.click()
        self.confirm_delivery_button.click()

    def quote_document_button(self, document: str) -> Locator:
        return self.page.get_by_role("button", name=document, exact=True)

    def download_quote_document(self, document: str) -> Download:
        with self.page.expect_download() as download_info:
            self.quote_document_button(document).click()
        return download_info.value

    def bind_policy(self) -> None:
        self.bind_policy_button.click()

    def policy_document_button(self, document: str) -> Locator:
        return (
            self.page.get_by_text(document, exact=True)
            .locator("xpath=ancestor::div[3]")
            .get_by_role("button")
        )

    def download_policy_document(self, document: str) -> Download:
        with self.page.expect_download() as download_info:
            self.policy_document_button(document).click()
        return download_info.value
