import os

from bs4 import BeautifulSoup
from decimal import Decimal as D

from ..base import BaseAccountScraper


class AustralianEthicalScraper(BaseAccountScraper):
    scrape_code = 'australianethical'
    default_currency = 'AUD'

    def login(self):
        self.browser.visit(
            'https://memberservices.australianethical.com.au/secure/InvestorCommunicationHistory.aspx'
        )
        user_elem = self.browser.find_by_css('input[id=txtMembershipNumber]')[0]
        pwd_elem = self.browser.find_by_css('input[id=txtPassword]')[0]
        self.browser.fill(user_elem['name'], os.getenv("AUTHETH_MEMBER_NUMBER"))
        self.browser.fill(pwd_elem['name'], os.getenv("AUTHETH_PASSWORD"))
        self.browser.find_by_css("input[id=btnLogin]").click()

    def scrape_account_details(self):
        self.browser.visit('https://memberservices.australianethical.com.au/secure/BalanceEstimate.aspx')
        elem = self.browser.find_by_css('div[id=divEstimateData]>table')[0]
        strings = [ss for ss in BeautifulSoup(elem.html).stripped_strings]

        account = self.create_account(name='default account')
        # switch sign because 28degrees lives in upside-down land
        account.balance = D(strings[-1].replace('$', '').replace(',', ''))

    def logout(self):
        self.browser.find_by_css('a[id=ancMemberLogout]').click()
