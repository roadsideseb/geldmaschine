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
            self.iframe.fill('f_username', os.getenv('UBANK_EMAIL'))
            self.iframe.fill('password', os.getenv('UBANK_PASSWORD'))
            self.iframe.find_by_css('input[name=Login]')[0].click()

            self.iframe.is_element_present_by_css(
                'div.tabularBorderAcctSumm>div>table',
                wait_time=10
            )

    def scrape_account_details(self):
        table_css = 'div.tabularBorderAcctSumm>div>table'

        # Make sure that content is fully loaded
        self.iframe.is_element_not_present_by_css(
            'span[class$=af_inputText_content]',
            1  # second
        )

        for elem in self.iframe.find_by_css(table_css):
            soup = BeautifulSoup(elem.html)
            strings = [ss for ss in soup.stripped_strings]
            bsb, account_number = strings[2].split('-')

            account = self.create_account(name=strings[0])
            account.number = account_number
            account.bank_code = "{}-{}".format(bsb[:3], bsb[3:])
            account.balance = D(strings[4].replace(',', '').replace('$', ''))

    def logout(self):
        pass
