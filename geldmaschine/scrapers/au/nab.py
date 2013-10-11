import os

from bs4 import BeautifulSoup
from decimal import Decimal as D

from ..base import BaseAccountScraper


class NabAccountScraper(BaseAccountScraper):
    scrape_code = 'nab'
    default_currency = 'AUD'

    def login(self):
        self.logger.debug('Filling in login details')
        self.browser.visit('https://ib.nab.com.au/nabib/mobile/login.ctl')
        self.browser.fill('userid', os.getenv('NAB_USERID'))
        self.browser.fill('password', os.getenv('NAB_PASSWORD'))
        self.browser.find_by_css('input[name=login]').click()

    def scrape_account_details(self):
        self.logger.debug('Retrieving account details')
        for row in self.browser.find_by_css('ul.account-list li>a'):
            strings = [ss for ss in BeautifulSoup(row.html).stripped_strings]
            bsb, acct_number = strings[1].split(' ')
            amount, typ = strings[-1].split(' ')
            if typ == 'DR':
                amount = '-{}'.format(amount)

            account = self.create_account(strings[0])
            account.bank_code = bsb
            account.number = acct_number
            account.balance = D(amount.replace(',', ''))

    def logout(self):
        self.browser.find_by_css("li.navlogout a")[0].click()
