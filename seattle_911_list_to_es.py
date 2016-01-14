import json
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://52.91.192.62:9200'])
infile = open('../data/Seattle_Police_Department_Police_Report_Incident.csv', "r")
for line in infile:
    keys=line.split(',')
    break

# res = es.delete(index='seattle', ignore=[400, 404])
# print res
cols_to_keep = [0, 6, 7, 8, 11, 12]
for line in infile:
    entry = line.split(',')
    lat = None
    lon = None
    obj={}
    for i in range(len(entry)):
            if i == 15:
                break #we don't use the higher indices, and the 'location field' is an embeded tuple, so len(keys)!=len(entry)
            if i is not 0:
                k = keys[i]
            else:
                k = 'id'

            if i in cols_to_keep:
                obj[k] = entry[i]
            elif i == 14:
                lon = float(entry[i])
            elif i == 15:
                lat = float(entry[i])

    obj['location'] = {
                "type":"point",
                "coordinates":[lon, lat]
            }
    res = es.index(index='seattle_911', doc_type='post', id=obj['id'], body=obj)
    #print res
