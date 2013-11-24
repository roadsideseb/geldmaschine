import os

from bs4 import BeautifulSoup
from decimal import Decimal as D

from ..base import BaseAccountScraper


class UbankAccountScraper(BaseAccountScraper):
    scrape_code = 'ubank'
    default_currency = 'AUD'

    def login(self):
        self.browser.visit('https://www.ubank.com.au')
        with self.browser.get_iframe('loginFrame') as self.iframe:
            self.iframe.is_element_present_by_css(
                'input[name=f_username]', wait_time=10)
            self.iframe.fill('f_username', os.getenv('UBANK_EMAIL'))
            self.iframe.fill('password', os.getenv('UBANK_PASSWORD'))

            self.find_and_click_by_css(self.iframe, 'input[name=Login]')

            self.iframe.is_element_present_by_css(
                'div.tabularBorderAcctSumm>div>table', wait_time=10)

    def scrape_account_details(self):
        table_css = 'table[id$=db1]'
        # Make sure that content is fully loaded
        self.iframe.is_element_not_present_by_css(table_css, 5)  # seconds

        for elem in self.iframe.find_by_css(table_css):
            self.logger.debug("Processing element")
            soup = BeautifulSoup(elem.html)
            strings = [ss for ss in soup.stripped_strings]
            bsb, account_number = strings[2].split('-')

            account = self.create_account(name=strings[0])
            account.number = account_number
            account.bank_code = "{}-{}".format(bsb[:3], bsb[3:])
            account.balance = D(strings[4].replace(',', '').replace('$', ''))
            self.logger.debug('Extracted {} from account {}'.format(
                account.balance, account.number))

    def logout(self):
        self.find_and_click_by_css(
            self.iframe, 'div[class=ActionLogout]>a', 10)
