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
        self.browser.visit('https://financepilot-pe.mlp.de/p10pepe/entry?rzid=XC&rzbk=0752&prt=report')

        alias_elem = self.browser.find_by_css('input[id=txtBenutzerkennung]')[0]
        password_elem = self.browser.find_by_css('input[type=password]')[0]

        self.browser.fill(alias_elem['name'], os.getenv('MLP_ALIAS'))
        self.browser.fill(password_elem['name'], os.getenv('MLP_PASSWORD'))
        self.browser.find_by_css('input[type=submit][value=Anmelden]').click()

        self.logger.debug('Change to account summary page')
        self.browser.find_by_css(u"li>a[title='Vermögensübersicht']").click()

    def scrape_account_details(self):
        self.logger.debug('Get account details')
        for row in self.browser.find_by_css('table[type=data]>tbody>tr'):
            if 'thd' in row.html or 'tft' in row.html:
                continue
            tds = [ss for ss in BeautifulSoup(row.html).stripped_strings]
            acct_name, acct_number = tds[:2]
            balance, currency = tds[-2:]

            account = self.create_account(acct_name, currency=currency)
            account.number = acct_number
            account.balance = D(balance.replace('.', '').replace(',', '.'))

    def logout(self):
        self.browser.find_by_css("div[class=logoutbutton]>a")[0].click()
