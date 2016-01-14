import json
from datetime import datetime

def datetime_from_raw(str_dt):
    return datetime.strptime(str_dt, "%Y-%m-%dT%H:%M:%S")

def main():
    d0 = json.load(open("../data/old_seattle.json", "r"))
    f_out = open("../data/old_seattle_timedeltas.csv","w")
    for line in d0['data']:
        value = float(line[15])
        action = line[13]
        lat = line[25]
        lon = line[26]
        dt1 = None if line[17]==None else datetime_from_raw(line[17])
        dt2 = None if line[18]==None else datetime_from_raw(line[18])
        dt3 = None if line[19]==None else datetime_from_raw(line[19])
        dt4 = None if line[20]==None else datetime_from_raw(line[20])
        if dt1 is not None:
            delta1 = None if dt2 is None else (dt2-dt1).days
            delta2 = None if dt3 is None else (dt3-dt1).days
            delta3 = None if dt4 is None else (dt4-dt1).days
        else:
            delta1 = None
            delta2 = None
            delta3 = None
        if dt2 is not None:
            delta4 = None if dt3 is None else (dt3-dt2).days
            delta5 = None if dt4 is None else (dt4-dt2).days
        else:
            delta4 = None
            delta5 = None
        if dt3 is not None:
            delta6 = None if dt4 is None else (dt4-dt3).days
        else:
            delta6 = None
        entry = [value, action, lat, lon, dt1, dt2, dt3, dt4, delta1, delta2, delta3, delta4, delta5, delta6]
        entry = map(lambda x: str(x), entry)
        f_out.write("\t".join(entry)+"\n")

if __name__ == "__main__":
    main()
