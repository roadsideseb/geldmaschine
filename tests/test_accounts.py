import json
import jsonschema

from unittest import TestCase

from geldmaschine.accounts import BaseAccount, SampleAccount


class TestAccount(TestCase):

    def test_account_serialization_to_json(self):
        print("ACCOUNT TEST")

        #account = BaseAccount()
        #print(account._fields)
        #print(account.schema)
        ##print(jsonschema.draft4_format_checker.check(account.schema()))

        #data = {
        #    'name': "A test name",
        #    'number': 1231312312312,
        #}
        #jsonschema.validate(data, account.schema)

        #print(json.dumps(account.schema, indent=4))



        account = SampleAccount()
        print(json.dumps(account.schema(), indent=4))
