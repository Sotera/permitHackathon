import json
import datetime
import re
import argparse
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from math import sqrt
import uuid
import elasticsearch

def to_date(in_str):
    y_pt = int(in_str[:4])
    m_pt = int(in_str[5:7])
    d_pt = int(in_str[8:])
    return datetime.date(y_pt, m_pt, d_pt)

class singleton_id:
    def __init__(self):
        self.index = 0
        self.c_ind = 0

    def get_index(self):
        ret = self.index
        self.index = ret+1
        return ret

def datetime_to_es_format(date):
    return str(date)+"T"+str(12)+":"+str(0)+":"+str(0)+"Z"

def word_in_desc(desc, word):
    clean = re.sub('[^\w\s]', '',  desc.lower())
    if clean.find(word) == -1:
        return False
    return True

def assign_to_cluster(recordList, epsilon, n_min):
    lalo = []
    for line in recordList:
        lalo.append([line.lon, line.lat])

    X = StandardScaler().fit_transform(lalo)
    fitObj = StandardScaler().fit(lalo)
    #laEps = epsilon/fitObj.std_[0]
    #loEps = epsilon/fitObj.std_[1]
    #fitEps = sqrt(laEps*laEps+loEps*loEps)
    fitEps = epsilon
    db = DBSCAN(eps=fitEps, min_samples=n_min).fit(X)
    for ind in range(len(recordList)):
        recordList[ind].cluster = db.labels_[ind]

class ScoreRecord:
    def __init__(self, record, uid, keyword, cType):
        lRec = record.lower().split("\t")
        self.id = uid
        #self.type = lRec[0]
        self.address = lRec[1]
        self.desc = lRec[2]
        self.category = lRec[3]
        self.action = lRec[4]
        self.work = lRec[5]
        self.value = float(lRec[6])
        self.name = lRec[7]
        self.apDt = None
        if lRec[8] != '':
            self.apDt = to_date(lRec[8])
        self.isDt = None
        if lRec[9] != '':
            self.isDt = to_date(lRec[9])
        self.isDt = lRec[9]
        self.status = lRec[10]
        self.contractor = lRec[11]
        self.lat = float(lRec[12])
        self.lon = float(lRec[13])
        self.cluster = -1
        self.c_id = None
        self.hasKeyword = False
        if cType==0:
            self.hasKeyword = word_in_desc(self.action, keyword)
        elif cType==1:
            self.hasKeyword = word_in_desc(self.category, keyword)
        elif cType==2:
            self.hasKeyword = word_in_desc(self.contractor, keyword)
        self.apQY = None
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

class ScoreBin:
    def __init__(self, record=None, hashtag=""):
        self.records = []
        self.n_clusters = -1
        self.tag = hashtag
        if record is not None:
            self.records.append(record)

    def add_record(self, record):
        self.records.append(record)

    def to_dict(self):
        return {
            'nTotal': len(self.records)
        }


def main(input_file, keyword, es, cType):
    d0 = open(input_file, 'r')
    j = 0
    err = set()
    id_gen = singleton_id()
    quarter_dict = {}
    for line in d0:
        try:
            j = j+1
            rec = ScoreRecord(line, id_gen.get_index(), keyword, cType)
            print rec.contractor
            k = str(rec.apQY)
            if k in quarter_dict.keys():
                quarter_dict[k].add_record(rec)
            else:
                quarter_dict[k] = ScoreBin(rec)
        except:
            err.add(j)
            continue

    for k, v in quarter_dict.iteritems():
        if k == 'None':
            continue
        if float(k)>2009.75:
            clusts = filter(lambda x: x.hasKeyword==True, v.records)
            assign_to_cluster(v.records, 0.001, 4)
            clusts = filter(lambda x: x.cluster!=-1, clusts)
            if len(clusts) is not 0:
                cid = str(uuid.uuid4())
                first = None
                b_first = True
                minVal = 99999999
                maxVal = 0
                minDate = datetime.date(3000, 1, 1)
                maxDate = datetime.date(1999, 1, 1)
                for c in clusts:
                    if b_first==True:
                        b_first=False
                        first = c
                    c.c_id = cid
                    if c.value < minVal:
                        minVal = c.value
                    if c.value > maxVal:
                        maxVal = c.value
                    if c.apDt < minDate:
                        minDate = c.apDt
                    if c.apDt > maxDate:
                        maxDate = c.apDt

                    c.write_to_es(es, 'hackathon_records', 'post')
                body = {
                    "tag":keyword,
                    "post_date":k,
                    "min_application_date":datetime_to_es_format(minDate),
                    "max_application_date":datetime_to_es_format(maxDate),
                    "num_posts":len(clusts),
                    "min_val":minVal,
                    "max_val":maxVal,
                    "location":{
                        "type":"point",
                        "coordinates":[first.lon, first.lat]
                    }
                }
                es.index(index='hackathon_clusts', doc_type='post', id=cid, body=json.dumps(body))




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Directory or file name (e.g. 'hdfs://domain.here.dev:/pathToData/")
    parser.add_argument("keyword", help="Keyword to perform clustering on")
    parser.add_argument("-epsilon", help="Fit epsilon, default 0.0001", type=float, default=0.001)
    parser.add_argument("-es_url", help="Elasticsearch url, default=http://localhost:9200", default=None)
    parser.add_argument("-cType", help="Type of clustering: 0 = Action (Default), 1 = category, 2 = contractor", type=int, default=0)
    args = parser.parse_args()

    es = None
    if args.es_url == None:
        es = elasticsearch.Elasticsearch()
    else:
        es = elasticsearch.Elasticsearch([args.es_url])

    main(args.input_file, args.keyword, es, args.cType)
