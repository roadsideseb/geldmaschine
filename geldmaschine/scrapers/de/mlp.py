#! -*- coding: utf-8 -*-
import os
import re

from bs4 import BeautifulSoup
from decimal import Decimal as D

from ..base import BaseAccountScraper


class MlpAccountScraper(BaseAccountScraper):
    scrape_code = 'mlp'
    default_currency = 'EUR'

    BALANCE_RE = re.compile(r'[0-9]{,3}(.[0-9]{3})*,[0-9]{2}')

    def login(self):
        self.logger.debug('Filling in logging details')
        self.browser.visit(
            'https://financepilot-pe.mlp.de/entry?appid=EBPE&amp;bankid=XC0752&amp;prt=report')

        username_input = 'input[id=txtBenutzerkennung]'
        self.browser.is_element_not_present_by_css(username_input, 10)

        alias_elem = self.ensure_element(
            self.browser.find_by_css(username_input))
        password_elem = self.ensure_element(
            self.browser.find_by_css('input[type=password]'))

        self.browser.fill(alias_elem['name'], os.getenv('MLP_ALIAS'))
        self.browser.fill(password_elem['name'], os.getenv('MLP_PASSWORD'))
        elem = self.browser.find_by_css('input[type=submit][value=Anmelden]')
        self.ensure_element(elem).click()

        self.logger.debug('Change to account summary page')
        self.find_and_click_by_css(
            self.browser, u"a[title='Financepilot Report']")

    def scrape_account_details(self):
        self.logger.debug('Get account details')

        subitem = "table[type='data']>tbody>tr"
        self.browser.is_element_not_present_by_css(subitem, 5)  # seconds

        for row in self.browser.find_by_css(subitem):
            tds = [ss for ss in BeautifulSoup(row.html).stripped_strings]
            if len(tds) < 5:
                continue
            acct_name, acct_number, __, balance, currency = tds[:5]
            # the header line doesn't contain a valid number in the
            if not self.BALANCE_RE.search(balance):
                continue
            account = self.create_account(acct_name, currency=currency)
            account.number = acct_number
            account.balance = D(balance.replace('.', '').replace(',', '.'))

    def logout(self):
        self.find_and_click_by_css(self.browser, "[title=Abmelden]")
