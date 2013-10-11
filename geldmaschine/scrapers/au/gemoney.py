import os

from bs4 import BeautifulSoup
from decimal import Decimal as D

from ..base import BaseAccountScraper


class GeMoneyAccountScraper(BaseAccountScraper):
    scrape_code = '28degrees'
    default_currency = 'AUD'

    def login(self):
        self.browser.visit(
            'https://28degrees-online.gemoney.com.au/access/login'
        )
        self.browser.fill('USER', os.getenv("GE28D_USERNAME"))
        self.browser.fill('PASSWORD', os.getenv("GE28D_PASSWORD"))
        self.browser.find_by_css("input[name=SUBMIT]").click()

    def scrape_account_details(self):
        elem = self.browser.find_by_css('span[name=accountSummaryTable]>table')
        strings = [ss for ss in BeautifulSoup(elem.html).stripped_strings]
        balance = D(strings[1].replace('$', ''))

        account = self.create_account(name='default account')
        # switch sign because 28degrees lives in upside-down land
        account.balance = -balance

    def logout(self):
        self.browser.find_by_css('ul#logout>li>a').click()
