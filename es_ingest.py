####start python with jars pointing to the elastic search jars
## ex if the jars are in /etc/spark/jars/elasticsearch-hadoop-2.2.1.jar
## pyspark --jars /etc/spark/jars/elasticsearch-hadoop-2.2.1.jar
from pyspark.sql import SQLContext
from datetime import date
import elasticsearch
import sys
import json
import time
sqlContext = SQLContext(sc)
today = str(date.today())
inputFiles = ["nyc/part-r-00001.parquet", "nyc/part-r-00002.parquet", "nyc/part-r-00003.parquet", \
				"nyc/part-r-00004.parquet", "nyc/part-r-00005.parquet", "cleveland/part-r-00001.parquet", \
				"cleveland/part-r-00002.parquet", "cleveland/part-r-00003.parquet", "cleveland/part-r-00004.parquet",\
				"texas/part-r-00001.parquet", "texas/part-r-00002.parquet", "texas/part-r-00003.parquet",\
				"texas/part-r-00004.parquet", "texas/part-r-00005.parquet", "texas/part-r-00006.parquet",\
				"texas/part-r-00007.parquet", "texas/part-r-00008.parquet", "texas/part-r-00009.parquet",\
				"texas/part-r-00010.parquet", "texas/part-r-00011.parquet", "texas/part-r-00012.parquet",\
				"texas/part-r-00013.parquet", "texas/part-r-00014.parquet", "texas/part-r-00015.parquet",\
				"texas/part-r-00016.parquet", "texas/part-r-00017.parquet", "texas/part-r-00018.parquet",\
				"texas/part-r-00019.parquet", "texas/part-r-00020.parquet", "texas/part-r-00021.parquet",\
				"texas/part-r-00022.parquet", "texas/part-r-00023.parquet", "texas/part-r-00024.parquet",\
				"texas/part-r-00025.parquet", "texas/part-r-00026.parquet", "texas/part-r-00027.parquet",\
				"texas/part-r-00028.parquet", "texas/part-r-00029.parquet", "texas/part-r-00030.parquet",\
				"texas/part-r-00031.parquet", "texas/part-r-00032.parquet", "texas/part-r-00033.parquet",\
				"texas/part-r-00034.parquet", "texas/part-r-00035.parquet", "texas/part-r-00036.parquet",\
				"texas/part-r-00037.parquet", "texas/part-r-00038.parquet", "texas/part-r-00039.parquet",\
				"texas/part-r-00040.parquet", "texas/part-r-00041.parquet", "texas/part-r-00042.parquet",\
				"texas/part-r-00043.parquet", "texas/part-r-00044.parquet", "texas/part-r-00045.parquet",\
				"texas/part-r-00046.parquet", "texas/part-r-00047.parquet", "texas/part-r-00048.parquet",\
				"texas/part-r-00049.parquet", "texas/part-r-00050.parquet"]
#inputFiles = [
es = elasticsearch.Elasticsearch()  # use default of localhost, port 9200

#ind = 9514914
ind = 0
check_ind = 0
checkpoints = [100, 1000, 3500, 10000, 35000, 1000000, 3500000, 10000000, 35000000, 100000000, 350000000, 1000000000]
log_file = open("processing_log_trial0.txt", "w", 0)
for inputFile in inputFiles:
	#print "processing:", inputFile
	records = sqlContext.read.parquet(inputFile)
	mapped = records.map(lambda x: \
		{"source":x.source, \
		"imageUrl":x.img, \
		"indexedDate":today, \
		"user":x.user, \
		"post_date":str(x.dt.date()), \
		"message":x.text, \
		"location":{"type":"point", "coordinates":[x.lon,x.lat]} \
		}\
	)
	
	items = mapped.collect()
	n_err = 0
	n_file = 0
	if ind == 0:
		start = time.time()
	for item in items:
		try:
			if ind == checkpoints[check_ind]:
				count = es.count(index='geqe', doc_type='post')["count"]
				while count < ind:
					count = es.count(index='geqe', doc_type='post')["count"]				
				delta = time.time() - start
				log_file.write("***\n* itterator count:\t" + str(ind) + "\n* indexed count:\t" + str(count) + "\n* time:\t" + str(delta) + "\n\n")
				check_ind = check_ind+1
			n_file = n_file + 1
			es.index(index='geqe', doc_type='post', id=ind, body=json.dumps(item), request_timeout=600)
			ind = ind+1
		except:
			print "Error inserting data (most likely timeout)", ind, "on", n_file, "record of file", inputFile
			print sys.exc_info()
			n_err = n_err + 1
			if n_err < 10:
				time.sleep(10)
			else:
				n_err = 0
				time.sleep(30)
			continue
	
	mapped.unpersist()
	print "****COMPLETED FILE*****", inputFile
	if inputFile == "texas/part-r-00050.parquet" and check_ind < len(checkpoints):
		while check_ind < len(checkpoints):
			count = es.count(index='geqe', doc_type='post')["count"]
			if count > checkpoints[check_ind]:
				delta = time.time() - start
				log_file.write("***\n* itterator count:\t" + str(ind) + "\n* indexed count:\t" + str(count) + "\n* time:\t" + str(delta) + "\n\n")
				check_ind = check_ind+1
	