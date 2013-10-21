============
Geldmaschine
============

.. image:: https://travis-ci.org/elbaschid/geldmaschine.png?branch=master
        :target: https://travis-ci.org/elbaschid/geldmaschine

.. image:: https://pypip.in/d/geldmaschine/badge.png
        :target: https://crate.io/packages/geldmaschine?version=latest

Travelling around and living in different countries has lead to me having bank
account in a few countries. Checking the balances for each account in each
country is teadious and boring. As a developer with an appreciation for TDD,
I've used tools like `splinter`_ and the underlying `selenium`_ for testing and
though it would be a great fit for automating the process.

What this little tool currently does:

* List all the available account scrapers.
* Scrape the account balance for one of all configured accounts.
* Print a summary (including converted currencies) to the console.

Installation
------------

It's not yet on PyPI and the handling of account credentials is not handled
nicely, yet. But with that, I'll add some installation instructions.


Supported Banks
---------------

* Germany
  ** MLP
  ** Deutsche Bank

* Australia
  ** NAB
  ** UBank
  ** 28degrees
  ** Australian Ethical

* Canada
  ** Coast Capital

License
-------

``geldmaschine`` is released under the `MIT license`_.

.. _`MIT license`: https://github.com/elbaschid/geldmaschine/blob/master/LICENSE

