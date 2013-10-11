#! /usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Geldmachine

Usage:
    geldmaschine list [--debug]
    geldmaschine all [--debug] [-d <webdriver>]
    geldmaschine check [--debug] [-d <webdriver>] <bank_code> ...
    geldmaschine -h | --help
"""
import logging
import pkgutil
import requests

from docopt import docopt
from blessings import Terminal
from decimal import Decimal as D
from babel.numbers import format_currency

from geldmaschine.scrapers.base import BaseAccountScraper

logger = logging.getLogger('geldmaschine')

term = Terminal()


CURRENCY_URL = 'http://rate-exchange.appspot.com/currency?from={fc}&to={tc}'


class Geldmachine(object):

    def __init__(self, driver='phantomjs', debug=False):
        self.driver = driver
        self.debug = debug

        self.browsers = []

        self.display_currency = 'AUD'
        self.conversion_rates = {}
        self.scrapers = {}

        self.load_scrapers()

    def __del__(self):
        if not self.debug:
            [b.quit() for b in self.browsers]

    def _load_scraper(self, name):
        mod_name, class_name = name.rsplit('.', 1)
        try:
            module = __import__(mod_name, fromlist=[class_name])
        except ImportError:
            raise RuntimeError(
                ("Importing scraper '{0}' failed, please check your "
                 "settings and try again.").format(name)
            )
        scraper_class = getattr(module, class_name)
        self.scrapers[scraper_class.scrape_code] = scraper_class
        return self.scrapers[scraper_class.scrape_code]

    def get_scrapers(self, scraper_pkg):
        module = pkgutil.get_loader(scraper_pkg).load_module()
        for __, submodname, ispkg in pkgutil.iter_modules(module.__path__):
            subpkg = "{}.{}".format(scraper_pkg, submodname)
            if ispkg:
                logger.debug('Loading package {0}'.format(submodname))
                self.get_scrapers(subpkg)
            else:
                logger.debug('Loading module {0}'.format(submodname))
                __import__(subpkg)

    def load_scrapers(self):
        scraper_pkgs = ['geldmaschine.scrapers']
        for scraper_pkg in scraper_pkgs:
            self.get_scrapers(scraper_pkg)
        for sc in BaseAccountScraper.__subclasses__():
            self.scrapers[sc.scrape_code] = sc

    def list(self):
        print(term.blue("=" * 50))
        print(term.blue("{0:15}{1}".format("Scaper ID", "Class")))
        print(term.blue("=" * 50))

        for code, klass in self.scrapers.items():
            print("{term.green}{0:15}{term.normal}{1}".format(
                code,
                klass.__name__,
                term=term
            ))
        print(term.blue("=" * 50))

    def check_banks(self, bank_codes=None):
        accounts = {}
        bank_codes = bank_codes or self.scrapers.keys()

        # closing the browsers from within the scraper will close the
        # connection to the selenium driver(s), we therefore need to collect
        # the browsers and close them at the end.
        self.browsers = []

        for code in bank_codes:
            scraper = self.scrapers[code](self.driver)
            scraper.dont_quit = True  # prevent selenium from shutting down
            scraper.run()
            accounts[scraper.get_name()] = scraper.get_accounts()
            self.browsers.append(scraper.browser)

        self.print_summary(accounts)

    def print_scrapers(self):
        for scrape_code, scraper_class in self.scrapers.iteritems():
            name = getattr(scraper_class, 'name', scraper_class.__name__)
            print(u'{}:\n\t{}\n'.format(scrape_code, name))

    def print_summary(self, accounts):
        self.get_conversion_rates(accounts)

        balances = []
        for bank_name in sorted(accounts.keys()):
            print(term.bold(bank_name))
            print(term.bold(u'-' * len(bank_name)))
            print()

            for account in accounts[bank_name].values():
                base_msg = [
                    u"{acct_name:40}{t.bold}{acct_balance:>20}",
                ]
                cbalance = account.balance
                if account.currency != self.display_currency:
                    conversion_rate = self.conversion_rates[account.currency]
                    cbalance = (account.balance * conversion_rate)
                    base_msg.append(u'{cbalance:>20}')

                base_msg.append(u"{t.normal}")

                balances.append(cbalance)

                if account.balance < 0:
                    base_msg = [u"{t.red}"] + base_msg
                else:
                    base_msg = [u"{t.green}"] + base_msg

                print(u''.join(base_msg).format(
                    acct_name=account.name,
                    acct_balance=format_currency(
                        account.balance,
                        account.currency
                    ),
                    t=term,
                    cbalance=format_currency(cbalance, self.display_currency),
                ))
            print()

        print()
        print(term.bold(u'=' * 80))
        msg = u"{:40}{t.bold}{t.gray}{balance:>40}{t.normal}"
        print(msg.format(
            'Sum Total',
            balance=format_currency(sum(balances), self.display_currency),
            t=term
        ))

    def get_conversion_rates(self, accounts):
        currencies = set()
        for acct_dict in accounts.values():
            for account in acct_dict.values():
                if account.currency != self.display_currency:
                    currencies.add(account.currency)
        for currency in currencies:
            try:
                rsp = requests.get(
                    CURRENCY_URL.format(
                        fc=currency,
                        tc=self.display_currency
                    )
                )
            except Exception:
                logger.error(
                    "could not retrieve currency {} conversion rate".format(
                        currency
                    )
                )
            self.conversion_rates[currency] = D(rsp.json().get('rate', D('0')))


def main():
    arguments = docopt(__doc__, version='Naval Fate 2.0')

    print(arguments)

    if arguments.get('--debug'):
        logging.basicConfig(level=logging.DEBUG)

    gm = Geldmachine(
        driver=arguments.get('<webdriver>') or 'phantomjs',
        debug=arguments.get('--debug', False)
    )

    if arguments.get('list'):
        gm.list()

    if arguments.get('all'):
        gm.check_banks()

    if arguments.get('check'):
        gm.check_banks(arguments.get('<bank_code>', []))


if __name__ == "__main__":
    main()
