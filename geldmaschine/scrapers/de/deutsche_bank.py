import os

from bs4 import BeautifulSoup
from decimal import Decimal as D

from ..base import BaseAccountScraper


class DeutscheBankAccountScraper(BaseAccountScraper):
    scrape_code = 'deutsche'
    default_currency = 'EUR'

    def login(self):
        self.logger.debug('Filling in logging details')
        self.browser.visit('https://meine.deutsche-bank.de/trxm/db/nextStepsLogin.do?selector=login')
        self.browser.fill('branch', os.getenv('DB_BRANCH'))
        self.browser.fill('account', os.getenv('DB_ACCOUNT'))
        self.browser.fill('pin', os.getenv('DB_PIN'))
        self.browser.find_by_css('input[type=submit]').click()

    def scrape_account_details(self):
        self.logger.debug('Get account details')
        for row in self.browser.find_by_css('table[summary]>tbody>tr:not([class~=subsequent])'):
            name, credit, balance, currency = [
                ss for ss in BeautifulSoup(row.html).stripped_strings
            ]
            account = self.create_account(name=name, currency=currency)
            account.number = os.getenv('DB_ACCOUNT')
            account.balance = D(balance.replace(',', ''))

    def logout(self):
        self.browser.find_by_css("a[href$='logout.do']")[0].click()
