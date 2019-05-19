import asyncio
import re
from collections import defaultdict
from itertools import chain
from json import load
from pathlib import Path
from tempfile import TemporaryFile

import aiohttp
from tinydb import Query, TinyDB

u = "https://www.pathofexile.com"
c = "POESESSID"
s = "8e3956244b1dcc9ee5e5c7654c84125f"

db_loc = Path("~/.pystash").expanduser()
db_loc.mkdir(exist_ok=True)

# TinyDB
db = TinyDB(db_loc / "poe.json")
db.purge_table("tabs")
tabs = db.table("tabs")
db.purge_table("items")
items = db.table("items")
Tab = Query()
Item = Query()

dps_types = {9, 10, 11}

re_stat_range = re.compile(r"Adds (\d+ to \d+) (.+)")
re_stat = re.compile(r"^(?:Gain )?([-+]?\d+(?:\.\d+)?)%? (?:to |of )?(.+)")
re_number = re.compile(r"\d+")


def avg(nums):
    return sum(map(int, nums)) / len(nums)


def process_item(e):
    # Lord help me
    try:
        calcs = []
        if "category" in e:
            if "currency" in e["category"]:
                return False
            if "maps" in e["category"]:
                return False
            # mps.append([{'group': k, 'category': v} for k, v in e['category'].items()][0])
        if "league" in e:
            del e["league"]
        if "verified" in e:
            del e["verified"]
        if "vaal" in e:
            del e["vaal"]
        if "frameType" in e:
            del e["frameType"]
        if "secDescrText" in e:
            del e["secDescrText"]
        if "descrText" in e:
            del e["descrText"]
        if "verified" in e:
            del e["verified"]
        if "flavourTextParsed" in e:
            del e["flavourTextParsed"]
        if "flavourText" in e:
            del e["flavourText"]
        if "requirements" in e:
            e["requirements"] = {i["name"]: float(i["values"][0][0]) for i in e["requirements"]}
            del e["requirements"]
        if "sockets" in e:
            # flatten the shape a bit, mostly ['sockets][i]['group'] becomes index in ['sockets'][i]
            # your group is your index in the list, and there will never be more than 6 groups
            ss = [{"seq": ""} for _ in range(6)]
            for s in e["sockets"]:
                ss[s["group"]]["seq"] += s["sColour"]
            ss = list(filter(lambda i: bool(i["seq"]), ss))
            for s in ss:
                s["size"] = len(s["seq"])
            e["sockets"] = ss
        if "properties" in e:
            if e["properties"]:
                ps = e["properties"]
                damage_types = []
                first = ps[0]
                if first["name"] and not first["values"] and first["displayMode"] == 0:
                    e["tags"] = first["name"].split(", ")
                    del ps[0]
                for p in ps:
                    v = p["values"][0][0]
                    if "type" in p:
                        # some properties need special processing, because they have a range of values and need the value of another property
                        if p["type"] in dps_types:
                            n = p["name"].split(" ")[0]
                            sum_avg_dmg = sum(map(avg, (v[0].split("-") for v in p["values"])))
                            damage_types.append((n, sum_avg_dmg))
                            calcs.append({"name": p["name"].title(), "value": sum_avg_dmg})
                            continue
                            # capture a value to use in later calculation
                        elif p["type"] == 13:
                            aps = float(v)
                            calcs.append({"name": "Attacks Per Second", "value": aps})
                            continue
                    r = re_number.findall(v)
                    calcs.append({"name": p["name"].title(), "value": float(r[0]) if r else v})
                dps = 0.0
                for n, v in damage_types:
                    d = v * aps
                    dps += d
                    calcs.append({"name": f"{n} DPS", "value": d})
                if dps:
                    calcs.append({"name": "DPS", "value": dps})
                del e["properties"]
        if "implicitMods" in e:
            if e["implicitMods"]:
                for i, m in enumerate(e["implicitMods"]):
                    m = m.replace("\n", " ")
                    r = re_stat.match(m)
                    if r:
                        g = r.groups()
                        calcs.append({"name": g[1].title(), "value": float(g[0])})
                        e["implicitMods"][i] = False
                        continue
                    r = re_stat_range.match(m)
                    if r:
                        g = r.groups()
                        calcs.append({"name": g[1].title(), "value": avg(g[0].split(" to "))})
                        e["implicitMods"][i] = False
                        continue
                e["implicitMods"] = list(filter(None, e["implicitMods"]))
        if "gems" not in e["category"] and "explicitMods" in e:
            if e["explicitMods"]:
                for i, m in enumerate(e["explicitMods"]):
                    m = m.replace("\n", " ")
                    r = re_stat.match(m)
                    if r:
                        g = r.groups()
                        calcs.append({"name": g[1].title(), "value": float(g[0])})
                        e["explicitMods"][i] = False
                        continue
                    r = re_stat_range.match(m)
                    if r:
                        g = r.groups()
                        calcs.append({"name": g[1].title(), "value": avg(g[0].split(" to "))})
                        e["explicitMods"][i] = False
                        continue
                e["explicitMods"] = list(filter(None, e["explicitMods"]))
        if "socketedItems" in e:
            if e["socketedItems"]:
                # for i in filter(None, map(process_item, e['socketedItems'])):
                #     items.replace_one({'id': i['id']}, i, {'upsert': True})
                # for i in filter(None, map(process_item, e['socketedItems'])):
                #     items.upsert(i, Item.id == i['id'])
                items.insert_multiple(list(filter(None, map(process_item, e["socketedItems"]))))
            del e["socketedItems"]
        e["mods"] = calcs
        return e
    except Exception as exptn:
        raise type(exptn)(*exptn.args, e).with_traceback(exptn.__traceback__)


# TinyDB.table_class = SmartCacheTable

# TinyMongo
# connection = TinyMongoClient(db_loc / 'poe')
# db = connection.poe
# items = db.items
# tabs = db.tabs


async def get_tab(session, tab_id, p, semaphore):
    async with semaphore:
        async with session.get(
            f"{u}/character-window/get-stash-items", params={"tabIndex": tab_id, **p}
        ) as r:
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
                items.insert_multiple(list(filter(None, map(process_item, load(t_file)["items"]))))


async def get_stash_tabs():
    semaphore = asyncio.BoundedSemaphore(10)
    params: dict = {}
    async with aiohttp.ClientSession(cookies={c: s}) as session:
        # async with session.head(f'{u}/character-window/get-stash-items') as r:
        #     rate_policy = {k: v for k, v in zip(['limit', 'interval', 'timeout'],
        #                                         r.headers['X-Rate-Limit-Account'].split(',')[0].split(":"))}
        #     rate_state = {k: v for k, v in zip(['limit', 'interval', 'timeout'],
        #                                        r.headers['X-Rate-Limit-Account-State'].split(',')[0].split(":"))}
        async with session.get(f"{u}/character-window/get-account-name") as r:
            params.update(await r.json())
        params.update({"league": "Standard"})
        async with session.get(
            f"{u}/character-window/get-stash-items", params={**{"tabs": 1}, **params}
        ) as r:
            # for t in (await r.json())['tabs']:
            # tabs.replace_one({'id': t['id']}, t, {'upsert': True})
            tabs.insert_multiple((await r.json())["tabs"])

        # tabs_to_get = (i['i'] for i in tabs.find({'type': {'$in': ['NormalStash', 'PremiumStash', 'QuadStash']}}))
        tabs_to_get = (
            i["i"]
            for i in tabs.search(Tab.type.one_of(["NormalStash", "PremiumStash", "QuadStash"]))
        )

        await asyncio.gather(*(get_tab(session, t, params, semaphore) for t in tabs_to_get))


asyncio.run(get_stash_tabs())

# all categories
# print(set(chain.from_iterable(c.get('category') for c in items.search(Item.category.exists()))))

# all types
# print(set(chain.from_iterable(chain.from_iterable(c.get('category').values() for c in items.search(Item.category.exists())))))
