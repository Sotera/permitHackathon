import matplotlib.pyplot as plt
import numpy as np

fig, (ax) = plt.subplots(ncols=1, figsize=(8,4))
#x -> individual records for a histogram
#ax.hist(x, 20, histtype='stepfilled', facecolor='g')

#binned
#bins = [0, 1, 1000, 5000, 25000, 50000, 100000, 200000, 500000, 1000000, 10000000, 100000000]

#all_data -> list of lists of data

fig, (ax) = plt.subplots(ncols=1, figsize=(8,8))
bins = [0.1, 1, 10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000]
ax.hist(value, bins, histtype='stepfilled', facecolor='g')
plt.ylabel("N Permits")
plt.xlabel("Permit Value")
plt.yscale('log')
plt.xscale('log')

fig, (ax) = plt.subplots(ncols=1, figsize=(8,8))
ax.hist(fval, 20, histtype='stepfilled', facecolor='g')
plt.ylabel("N Permits")
plt.xlabel("Permit Value")
plt.yscale('log')
