import json
import datetime
import re
import argparse
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from math import sqrt
import uuid
import elasticsearch

def date_to_yq(dt):
    month = int(dt[:2])
    year = int(dt[6:10])
    frac = float(month/3)*.25 if month%3!=0 else float(month/3)*.25-.25
    return year + frac

def to_date(str_dt):
    return datetime.strptime(str_dt, "%m/%d/%Y %H:%M:%S %p")

class ScoreRecord:
    def __init__(self, record, uid, keyword):
        lRec = record.lower().split(",")
        self.id = lRec[0]
        self.type = lRec[4].split('-')[0]
        self.description = lRec[6]
        self.dt =
        if self.apDt is not None:
            dt = self.apDt
            q = float((dt.month/3 + 1) if dt.month%3!=0 else dt.month/3)
            self.apQY = dt.year + q*.25-.25

    def to_dict(self):
        obj = {
            'applicant': self.name,
            'contractor': self.contractor,
            'indexedDate': datetime_to_es_format(datetime.datetime.now()),
            'value': self.value,
            'action': self.action,
            'cluster_id': self.c_id,
            'applicationDate': str(self.apDt),
            'location':{
                "type":"point",
                "coordinates":[self.lon, self.lat]
            }
        }
        return obj

    def write_to_es(self, es, es_ind, es_type):
        es.index(index=es_ind, doc_type=es_type, id=self.id, body=json.dumps(self.to_dict()))

def main(input_file, keyword, es):
    d0 = open(input_file, "r")
    cols = []
    for line in d0:
        cs = line.split(",")
        for c in cs:
            cols.append(c)
        break

    d1 = []
    for line in d0:
        rec = ScoreRecord(line)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Directory or file name (e.g. 'hdfs://domain.here.dev:/pathToData/")
    parser.add_argument("keyword", help="Keyword to perform clustering on")
    parser.add_argument("-epsilon", help="Fit epsilon, default 0.0001", type=float, default=0.001)
    parser.add_argument("-es_url", help="Elasticsearch url, default=http://localhost:9200", default=None)
    args = parser.parse_args()

    es = None
    if args.es_url == None:
        es = elasticsearch.Elasticsearch()
    else:
        es = elasticsearch.Elasticsearch([args.es_url])

    main(args.input_file, args.keyword, es)