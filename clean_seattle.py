import re
import json
f_out = open("clean_seattle.csv", "w")
d0 =json.load(open("seattle.json", "r"))
i=-1
fails = set()
for line in d0["data"]:
    i = i+1
    try:
        trimmed = line[9:17]
        trimmed.append(None if line[17] == None else line[17][:10])
        trimmed.append(None if line[18] == None else line[18][:10])
        trimmed.extend(line[21:23])
        trimmed.extend(line[25:27])
        f_out.write("\t".join(map(lambda x: '' if type(x)==type(None) else re.sub('[^\w\s.-]','',x,flags=re.UNICODE), trimmed))+"\n")
    except:
        fails.add(i)