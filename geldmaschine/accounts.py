import re
import json

from collections import OrderedDict


class JsonField(object):
    name = None
    type = None
    title = None
    description = None

    @classmethod
    def schema(cls):
        schema = {'type': cls.type}
        if cls.title:
            schema['title'] = cls.title
        if cls.description:
            schema['description'] = cls.description
        return schema


class AnyField(JsonField):
    type = 'any'


class NullField(JsonField):
    type = 'null'


class NumberField(JsonField):
    type = 'number'


class IntegerField(JsonField):
    type = 'integer'


class StringField(JsonField):
    type = 'string'


class ListField(JsonField):
    type = 'array'

    def __init__(self, classes=None, subclasses_of=None):
        self.classes = classes or []
        self.base_classes = subclasses_of or []

    def schema(self):
        json_schema = super(ListField, self).schema()
        #TODO get all subclasses recursively for base_classes
        classes = set(self.classes)
        for bc in self.base_classes:
            for klass in bc.__subclasses__():
                classes.add(klass)
        json_schema['items'] = []
        for klass in classes:
            json_schema['items'].append({
                '$ref': klass.__name__
            })
        return json_schema


class AccountMetaClass(type):

    def __init__(cls, name, bases, nmspc):
        super(AccountMetaClass, cls).__init__(name, bases, nmspc)

        json_type, __ = re.subn('([A-Z])', '_\\1', name)
        json_type = json_type.lower()
        cls.type = json_type

        if not hasattr(cls, '_fields'):
            cls._fields = OrderedDict()

        for attr_name, attr_value in nmspc.items():
            if issubclass(attr_value.__class__, JsonField):
                attr_value.name = attr_name
                attr_value.parent_class = cls
                cls._fields[attr_name] = attr_value


class BaseAccount(metaclass=AccountMetaClass):
    name = StringField()
    number = StringField()
    bank_code = StringField()
    bank = StringField()
    country = StringField()

    balance = NumberField()
    currency = StringField()

    @classmethod
    def schema(cls):
        schema = OrderedDict(
            #"$schema": "http://json-schema.org/draft-04/schema",
            #"id": "http://jsonschema.net",
            id='#{0}'.format(cls.__name__),
            type="object",
            properties=OrderedDict(),
        )
        for name, value in cls._fields.items():
            schema['properties'][name] = value.schema()
        return schema


class SampleAccount(BaseAccount):
    subaccounts = ListField(subclasses_of=[BaseAccount])
