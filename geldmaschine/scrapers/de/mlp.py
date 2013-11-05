#! -*- coding: utf-8 -*-
import os

from bs4 import BeautifulSoup
from decimal import Decimal as D

from ..base import BaseAccountScraper


class MlpAccountScraper(BaseAccountScraper):
    scrape_code = 'mlp'
    default_currency = 'EUR'

    def login(self):
        self.logger.debug('Filling in logging details')
        self.browser.visit('https://financepilot.mlp.de')

        username_input = 'input[id=txtBenutzerkennung]'
        self.browser.is_element_not_present_by_css(username_input, 5)  # seconds
        alias_elem = self.browser.find_by_css(username_input)[0]
        password_elem = self.browser.find_by_css('input[type=password]')[0]

        self.browser.fill(alias_elem['name'], os.getenv('MLP_ALIAS'))
        self.browser.fill(password_elem['name'], os.getenv('MLP_PASSWORD'))
        self.browser.find_by_css('input[type=submit][value=Anmelden]').click()

        self.logger.debug('Change to account summary page')
        self.browser.find_by_css(u"a[title='Financepilot Banking']").click()

    def scrape_account_details(self):
        self.logger.debug('Get account details')
        for row in self.browser.find_by_css('table[id=tblUebersicht]>tbody>tr[class~=subItem]'):
            tds = [ss for ss in BeautifulSoup(row.html).stripped_strings]
            acct_name, acct_number, balance, currency = tds[:4]
            account = self.create_account(acct_name, currency=currency)
            account.number = acct_number

            balance, btype = balance.split(' ')
            if btype.lower() == 'h':
                balance = balance
            else:
                balance = "-{}".format(balance)
            account.balance = D(balance.replace('.', '').replace(',', '.'))

    def logout(self):
        self.browser.find_by_css("input[title=Abmelden]")[0].click()
