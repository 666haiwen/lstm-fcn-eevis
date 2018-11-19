import time
import h5py
import numpy as np

import sys
import os
sys.path.append(os.getcwd())
from data_parse import const as gl
from utils_data.cluster.numba_distance import euclidean, test_euclidean


def test_distance_cost():
    X = h5py.File(gl.ORIGNIL_SAMPLE_PATH + 'data\\orignal_sample.hdf5', 'r+')
    Q = X['ST_100'][:]
    C = X['ST_101'][:]
    time_a = time.time()
    for i in range(100):
        a = test_euclidean(Q, C)
    time_b = time.time()
    print((time_b - time_a)/100)
    print(a)    

    for i in range(100):
        a = euclidean(Q, C)
    time_b = time.time()
    print((time_b - time_a)/100)
    print(a)
    X.close()

# test_distance_cost()

a = np.ones((10000,10000))
del(a)
print(a)
