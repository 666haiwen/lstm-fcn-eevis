import time
import h5py
import numpy as np

import sys
import os
sys.path.append(os.getcwd())
from data_parse import const as gl
from utils_data import const as st
from utils_data.cluster.canopy import Canopy
from utils_data.cluster.numba_distance import *
from utils_data.cluster.dataset import Dataset


def test_distance_cost():
    X = h5py.File(gl.ORIGNIL_SAMPLE_PATH + 'data\\orignal_sample.hdf5', 'r+')
    Q = X['ST_100'][:]
    C = X['ST_101'][:]
    time_a = time.time()
    # for i in range(100):
    #     a = test_euclidean(Q, C)
    # time_b = time.time()
    # print((time_b - time_a)/100)
    # print(a)    

    for i in range(100):
        a = euclidean(Q, C, gl.FEATRUE_NUMBER)
    time_b = time.time()
    print((time_b - time_a)/100)
    print(a)
    X.close()

def test_canopy():
    sample_path = gl.ORIGNIL_SAMPLE_PATH + 'data\\orignal_sample.hdf5'
    batch_path = gl.ORIGNIL_SAMPLE_PATH + 'data\\batch_sample.hdf5'
    shape = (gl.TIMES_STEPS, gl.FEATRUE_NUMBER)
    X = Dataset(sample_path, batch_path, st.BATCH_HDF5, gl.ORIGNIL_SAMPLE_NUM, shape)
    x = Canopy(X, 0.6, 0.4, sts)
    x.fit()
    canopy, index = x.get_canopy()


def set_dis_matrix(parameter_list):
    pass


# test_distance_cost()

# test_canopy()
