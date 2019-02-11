import asyncio
from collections import defaultdict
from itertools import chain
from json import load

import aiohttp
from tinydb import TinyDB, Query
from tinymongo import TinyMongoClient
from pathlib import Path
from tempfile import TemporaryFile

u = 'https://www.pathofexile.com'


def process_item(e):
    if 'category' in e:
        if 'currency' in e['category']:
            return False
        if 'maps' in e['category']:
            return False
    if 'league' in e:
        del e['league']
    if 'verified' in e:
        del e['verified']
    if 'frameType' in e:
        del e['frameType']
    if 'secDescrText' in e:
        del e['secDescrText']
    if 'descrText' in e:
        del e['descrText']
    if 'verified' in e:
        del e['verified']
    if 'flavourTextParsed' in e:
        del e['flavourTextParsed']
    if 'flavourText' in e:
        del e['flavourText']
    if 'requirements' in e:
        e['mapped_requirements'] = {i['name']: i['values'][0][0] for i in e['requirements']}
        # del e['requirements']
    if 'sockets' in e:
        ss = defaultdict(lambda: defaultdict(str))
        for s in e['sockets']:
            ss[str(s['group'])]['seq'] += s['sColour']
        for g, s in ss.items():
            ss[g]['size'] = len(s['seq'])
        e['mapped_sockets'] = ss
    if 'properties' in e:
        if e['properties']:
            first = e['properties'][0]
            if first['name'] and not first['values'] and first['displayMode'] == 0:
                e['tags'] = first['name'].split(', ')
            e['named_properties'] = {i['name']: i["values"][0][0]
                                     for i in e['properties'] if i["values"] and 'name' in i}
            e['typed_properties'] = {i['type']: i["values"][0][0]
                                     for i in e['properties'] if i["values"] and 'type' in i}
            # del e['properties']
    if 'socketedItems' in e:
        if e['socketedItems']:
            # for i in filter(None, map(process_item, e['socketedItems'])):
            #     items.replace_one({'id': i['id']}, i, {'upsert': True})
            # for i in filter(None, map(process_item, e['socketedItems'])):
            #     items.upsert(i, Item.id == i['id'])
            items.insert_multiple(list(filter(None, map(process_item, e['socketedItems']))))
        del e['socketedItems']
    return e


# TinyDB.table_class = SmartCacheTable
db_loc = Path('~/.pystash').expanduser()
db_loc.mkdir(exist_ok=True)

# TinyMongo
# connection = TinyMongoClient(db_loc / 'poe')
# db = connection.poe
# items = db.items
# tabs = db.tabs

# TinyDB
db = TinyDB(db_loc / 'poe.json')
db.purge_table('tabs')
tabs = db.table('tabs')
db.purge_table('items')
items = db.table('items')
Tab = Query()
Item = Query()


async def get_tab(session, tab_id, p, semaphore):
    async with semaphore:
        async with session.get(f'{u}/character-window/get-stash-items', params={'tabIndex': tab_id, **p}) as r:
            with TemporaryFile() as t_file:
                while True:
                    chunk = await r.content.read(64)
                    if not chunk:
                        break
                    t_file.write(chunk)
                t_file.seek(0)

                # for i in filter(None, map(process_item, load(t_file)['items'])):
                #     items.replace_one({'id': i['id']}, i, {'upsert': True})
                # for i in filter(None, map(process_item, load(t_file)['items'])):
                #     items.upsert(i, Item.id == i['id'])
                items.insert_multiple(list(filter(None, map(process_item, load(t_file)['items']))))


async def get_stash_tabs():
    semaphore = asyncio.BoundedSemaphore(10)
    params: dict = {}
    async with aiohttp.ClientSession(cookies={c: s}) as session:
        # async with session.head(f'{u}/character-window/get-stash-items') as r:
        #     rate_policy = {k: v for k, v in zip(['limit', 'interval', 'timeout'],
        #                                         r.headers['X-Rate-Limit-Account'].split(',')[0].split(":"))}
        #     rate_state = {k: v for k, v in zip(['limit', 'interval', 'timeout'],
        #                                        r.headers['X-Rate-Limit-Account-State'].split(',')[0].split(":"))}
        async with session.get(f'{u}/character-window/get-account-name') as r:
            params.update(await r.json())
        params.update({'league': "Standard"})
        async with session.get(f'{u}/character-window/get-stash-items', params={**{'tabs': 1}, **params}) as r:
            # for t in (await r.json())['tabs']:
                # tabs.replace_one({'id': t['id']}, t, {'upsert': True})
            tabs.insert_multiple((await r.json())['tabs'])

        # tabs_to_get = (i['i'] for i in tabs.find({'type': {'$in': ['NormalStash', 'PremiumStash', 'QuadStash']}}))
        tabs_to_get = (i['i'] for i in tabs.search(Tab.type.one_of(['NormalStash', 'PremiumStash', 'QuadStash'])))

        await asyncio.gather(*(get_tab(session, t, params, semaphore) for t in tabs_to_get))


asyncio.run(get_stash_tabs())

# all categories
# print(set(chain.from_iterable(c.get('category') for c in items.search(Item.category.exists()))))

# all types
# print(set(chain.from_iterable(chain.from_iterable(c.get('category').values() for c in items.search(Item.category.exists())))))
