import sys
import os
import time
import json
import h5py

sys.path.append(os.getcwd())
from utils_data.kmeans import kmeans
from utils_data.numba_distance import *
from data_parse import const as gl


def cluster_test():
    X = h5py.File(gl.ORIGNIL_SAMPLE_PATH + 'data\\orignal_sample.hdf5', 'r+')
    before_time = time.time()
    funcList = [euclidean, related, sts, dtw, kullback_Liebler, base_LPC, pca_based]
    namelist = ['ST_' + str(i) for i in range(1, 2671)]
    # kmeans
    for func in funcList:
        before_time = time.time()
        labels, _ = kmeans(X, namelist, (len(namelist), gl.TIMES_STEPS, gl.FEATRUE_NUMBER), func)
        after_time = time.time()
        with open(gl.ORIGNIL_SAMPLE_PATH + 'data\\kmeans-' + func.__name__, 'w') as fp:
            json.dump({'labels': labels, 'time': after_time - before_time}, fp)
        print('Finish the kmeans of {},\n And the Time cost is {}'.\
        format(func.__name__, after_time - before_time))
    X.close()

cluster_test()
