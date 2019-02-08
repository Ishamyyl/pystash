from tinydb_smartcache import SmartCacheTable
from tinymongo import TinyMongoClient
from pprint import pprint

from itertools import chain

from json import load


def process(e):
    if 'verified' in e:
        del e['verified']
    # if 'frameType' in e:
    #     del e['frameType']
    if 'flavourText' in e:
        del e['flavourText']
    if 'flavourTextParsed' in e:
        del e['flavourTextParsed']
    if 'requirements' in e:
        e['requirements'] = {i['name']: i['values'][0][0] for i in e['requirements']}
    if 'properties' in e:
        e['propertiesType'] = {i['type']: i["values"][0][0] for i in e['properties'] if i["values"] and 'type' in i}
        e['propertiesName'] = {i['name']: i["values"][0][0] for i in e['properties'] if i["values"] and 'name' in i}
    return e


connection = TinyMongoClient('poe')
account = connection.account
account.table_class = SmartCacheTable
items = account.items


# with open('test.json') as f:
#     items.insert_many(list(map(process, load(f)['items'])))

# pprint(list(items.find({'frameType': 1})))

# all categories
print(set(chain.from_iterable(c.get('category') for c in items.find())))

# all types
print(set(chain.from_iterable(chain.from_iterable(c.get('category').values() for c in items.find()))))
