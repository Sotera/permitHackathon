import json
from elasticsearch import Elasticsearch

es = Elasticsearch(['localhost'])
infile =json.load(open('seattle.json', "r"))
keys = []
for col in infile['meta']['view']['columns']:
    keys.append(col['name'])

# res = es.delete(index='seattle', ignore=[400, 404])
# print res
for entry in infile['data']:
    obj={}

    for i in range(len(entry)):
        k = keys[i]
        if k != 'Location': # Location array has multiple data types
            obj[k] = entry[i]
    res = es.index(index='seattle', doc_type='permit', id=obj['id'], body=obj)
    print res
