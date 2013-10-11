import psutil
import logging

from splinter import Browser


class ScraperError(BaseException):
    pass


class Account(object):
    currency = None

    def __init__(self, name, currency):
        if not currency:
            raise ScraperError("No currency specified for account")

        self.currency = currency
        self.name = name
        self.bank_code = None
        self.number = None
        self.balance = None

    def fill(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)


class BaseAccountScraper(object):
    dont_quit = False
    scrape_code = None
    default_currency = None

    def __init__(self, driver_name='phantomjs'):
        self.driver_name = driver_name
        self.logger = logging.getLogger('geldspeicher')

        if not self.scrape_code:
            raise ScraperError("Scraper has no 'scrape_code' specified")

        webdriver_kwargs = {}
        if self.driver_name == 'phantomjs':
            webdriver_kwargs['service_args'] = ['--ignore-ssl-errors=true']
            self._store_processes()

        self.browser = Browser(self.driver_name, **webdriver_kwargs)

        self._accounts = {}

    def login(self):
        pass

    def logout(self):
        pass

    def scrape_account_details(self):
        pass

    def run(self):
        self.logger.info("Start running scraper {}".format(self.scrape_code))
        self.login()
        self.scrape_account_details()
        self.logout()
        self.logger.info("Finished running scraper {}".format(self.scrape_code))

    def get_accounts(self):
        return self._accounts

    def create_account(self, name, currency=None):
        account = Account(name, currency=currency or self.default_currency)
        self._accounts[name] = account
        return account

    def get_name(self):
        return getattr(self, 'name', self.__class__.__name__)

    def __del__(self):
        if self.dont_quit:
            return

        self.logger.debug("quitting browser")
        self.browser.quit()
        if self.driver_name == 'phantomjs':
            self.logger.debug("kill started phantomjs processes")
            for process in psutil.process_iter():
                if process.name == 'phantomjs' \
                   and process.pid not in self._phantomjs_processes:
                    process.kill()

    def _store_processes(self):
        self._phantomjs_processes = [
            p.pid for p in psutil.process_iter() if p.name == 'phantomjs'
        ]
