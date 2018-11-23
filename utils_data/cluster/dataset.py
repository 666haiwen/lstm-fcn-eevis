# Authors: Chen zexian(zjuczx@zju.edu.cn)
import random
import os
import h5py
import json
import gc
import numpy as np
import data_parse.const as gl


def batchLabel(i):
    return 'batch_' + str(i)

def set_cheap_dis_matrix(x, y, x_id, y_id, dis_matrix, disfunc, minsize):
    len_x = len(x_id)
    len_y = len(y_id)
    for i in range(len_x):
        for j in range(len_y):
            dis_matrix[x_id[i]][y_id[j]] = \
            dis_matrix[y_id[j]][x_id[i]] = disfunc(x[i], y[j], minsize)


def get_dis_matrix(X, disfunc, minsize):
    # get cheap dis_matrix of samples
    if os.path.exists(gl.ORIGNIL_SAMPLE_PATH + 'data/dis_matrix.json'):
        f = open(gl.ORIGNIL_SAMPLE_PATH + 'data/dis_matrix.json', encoding='utf-8')
        dis_matrix = json.load(f)['dis']
        return dis_matrix
    dis_matrix = np.zeros((X.number, X.number))
    x = np.zeros((X.batchSize,) +  X.shape)
    y = np.zeros((X.batchSize,) +  X.shape)
    for i in range(X.batchNumber):
        x, x_id = X.get_batch(i, x)
        print('batch {} :'.format(i))
        set_cheap_dis_matrix(x, x, x_id, x_id, dis_matrix, disfunc, minsize)
        for j in range(i+1, X.batchNumber):
            print(j)
            y, y_id = X.get_batch(j, y)
            set_cheap_dis_matrix(x, y, x_id, y_id, dis_matrix, disfunc, minsize)
    
    del x
    del y
    gc.collect()
    np.savetxt(gl.ORIGNIL_SAMPLE_PATH + 'data/dis_matrix.txt', dis_matrix, fmt='%.8f')
    # with open(gl.ORIGNIL_SAMPLE_PATH + 'data/dis_matrix.json', 'w') as fp: 
    #     json.dump({'dis': dis_matrix.tolist()}, fp)
    print('Writing dis_matrix Finish!')
    return dis_matrix


class Dataset(object):
    """Dataset of hdf5 files

    sample: hdf5 file of sample saved

    batch: hdf5 file of group in batch saved

    batchSize: the size of batch

    number: the number of sample in hdf5 file

    shape: the shape of each sample in file

    namelist: the name of sample in the file such as 'ST_1'

    batchlist: the name of group in the file
    """
    def __init__(self, sample_path, batch_path, batchSize, number, shape):
        self.sample =h5py.File(sample_path, 'r')
        self.batch =h5py.File(batch_path, 'r')
        self.batchSize = batchSize
        self.number = number
        self.shape = shape
        self.namelist = ['ST_' + str(i) for i in range(number)]
        random.shuffle(self.namelist)
        self.batchlist = {}
        tmp = []
        batch_number = 0
        for i in range(number):
            tmp.append(self.namelist[i])
            if len(tmp) == batchSize:
                self.batchlist['batch_' + str(batch_number)] = tmp.copy()
                tmp = []
                batch_number += 1
        if tmp is not None:
            self.batchlist[batchLabel(batch_number)] = tmp.copy()
            batch_number += 1
        self.batchNumber = batch_number
    

    def get_batch(self, i, x):
        shape = (self.batchSize, self.shape[0], self.shape[1])
        if x.shape != shape:
            raise ValueError('The shape to read batch in Dataset is not equal, expected {} but received {}'.format(shape, x.shape))
        name = batchLabel(i)
        namelist = []
        for i, key in enumerate(self.batch[name].keys()):
            self.batch[name][key].read_direct(x[i])
            namelist.append(int(key[3:]))
        return x, namelist

    def get_sample_by_batch(self, namelabel, x):
        name = 'ST_' + str(namelabel)
        self.batch[namelabel / self.batchSize][name].read_direct(x)
    
    def get_sample_by_name(self, name, x):
        self.sample[name].read_direct(x)
    