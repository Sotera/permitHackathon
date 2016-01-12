import re
import json
d0 =json.load(open("seattle.json", "r"))
d1 = {}
d2 = {}
keys = []
for col in d0['meta']['view']['columns']:
    keys.append(col['name'])

for entry in d0['data']:
    ll_key = entry[10]
    if ll_key not in d1.keys():
        d1[ll_key] = []
    a = {}
    for ind in range(len(entry)):
        a[keys[ind]] = entry[ind]
    d1[ll_key].append(a)

for k, v in d1.iteritems():
    if len(v) > 1:
        d2[k] = v