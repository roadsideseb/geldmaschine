import os
import re

from bs4 import BeautifulSoup
from decimal import Decimal as D

from ..base import BaseAccountScraper


class CoastCapitalScraper(BaseAccountScraper):
    scrape_code = 'coast_capital'
    default_currency = 'CAD'

    def login(self):
        self.browser.visit('https://www.coastcapitalsavings.com/Personal/')

        self.browser.fill('acctnum', os.getenv('CC_MEMBER_ID'))
        self.browser.find_by_css("input[title='Log in']").click()

        question = self.browser.find_by_css("label[for=answer]")[0].text

        #TODO: use the full questions here and make it work with all available
        # question types.
        if 'father' in question:
            self.browser.fill('answer', os.getenv('CC_FATHER'))
        elif 'grandmother' in question:
            self.browser.fill('answer', os.getenv('CC_GRANDMOTHER'))
        elif 'city' in question:
            self.browser.fill('answer', os.getenv('CC_CITY'))
        else:
            raise Exception("I don't have an answer for {}".format(question))

        self.browser.find_by_css('input[name=Continue]').click()
        self.browser.fill('pac', os.getenv('CC_PASSWORD'))
        self.browser.find_by_css('input[name=Continue]').click()

    def scrape_account_details(self):
        for row in self.browser.find_by_css('table[class~=summarydata] tr'):
            if '$' not in row.html:
                continue
            name, balance = [ss for ss in BeautifulSoup(row.html).stripped_strings]
            res = re.match(r'(?P<name>[^0-9]+) (?P<account_number>\d+)', name)

            account = self.create_account(name=res.group('name'))
            account.number = res.group('account_number')
            account.balance = D(balance.replace('$', '').replace(',', ''))

    def logout(self):
        self.browser.find_by_css('input[value=Logout]').click()
