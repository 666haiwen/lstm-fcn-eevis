import sys
import os
import h5py
import numpy as np
sys.path.append(os.getcwd())
import data_parse.const as gl
import utils_data.const as st


def addSt(fileName):
    X = h5py.File(gl.ORIGNIL_SAMPLE_PATH + 'data\\orignal_sample.hdf5', 'r+')
    if X.get(fileName) == None:
        path = gl.ORIGNIL_SAMPLE_PATH + fileName + '\\tensor2D.txt'
        x = np.loadtxt(path)
        X.create_dataset(fileName, shape=x.shape, data=x)
        print(fileName + ' has been add!')
    else:
        print(fileName + ' is already exist!')
    X.close()


def translateBatch(initValue):
    X = h5py.File(gl.ORIGNIL_SAMPLE_PATH + 'data\\orignal_sample.hdf5', 'r+')
    Y = h5py.File(gl.ORIGNIL_SAMPLE_PATH + 'data\\batch_sample.hdf5', 'w')
    namelist = ['ST_' + str(i) for i in range(2670)]
    readX = np.zeros((st.BATCH_HDF5, gl.TIMES_STEPS, gl.FEATRUE_NUMBER))
    batch_num = initValue
    while True:
        print('batch: {}'.format(batch_num))
        pre = batch_num * st.BATCH_HDF5
        end = min(2670, pre + st.BATCH_HDF5)
        diff = end - pre
        for j in range(diff):
            readX[j] = X[namelist[j + pre]][:]
        Y.create_dataset('batch_' + str(batch_num), shape=readX.shape, data=readX)
        if end >= 2670:
            break
        batch_num += 1
    X.close()
    Y.close()

# addSt('ST_0')
translateBatch(0)
#  0 - 534
#  534 - 1068