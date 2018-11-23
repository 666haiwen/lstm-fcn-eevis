import sys
import os
import time
import json
import h5py
from sklearn.manifold import TSNE

sys.path.append(os.getcwd())
from data_parse import const as gl
from utils_data import const as st
from utils_data.cluster.kmeans import kmeans
from utils_data.cluster.birch import Birch
from utils_data.cluster.numba_distance import *
from utils_data.cluster.dataset import get_dis_matrix, Dataset


def cluster_test():
    X = h5py.File(gl.ORIGNIL_SAMPLE_PATH + 'data\\orignal_sample.hdf5', 'r+')
    shape = (gl.TIMES_STEPS, gl.FEATRUE_NUMBER)
    before_time = time.time()
    funcList = [euclidean, related, sts, dtw, kullback_Liebler, base_LPC, pca_based]
    namelist = ['ST_' + str(i) for i in range(2671)]

    # # kmeans
    # for func in funcList:
    #     before_time = time.time()
    #     labels, _ = kmeans(X, namelist, (len(namelist), gl.TIMES_STEPS, gl.FEATRUE_NUMBER), func)
    #     after_time = time.time()
    #     with open(gl.ORIGNIL_SAMPLE_PATH + 'data\\kmeans-' + func.__name__ + '.json', 'w') as fp:
    #         json.dump({'labels': labels, 'time': after_time - before_time}, fp)
    #     print('Finish the kmeans of {},\n And the Time cost is {}'.\
    #     format(func.__name__, after_time - before_time))

    # Birch
    birch = Birch(n_clusters=None, threshold=np.sqrt(690), namelist=namelist, shape=shape)
    before_time = time.time()
    labels = birch.fit_predict(X)
    n_cluster = np.max(labels) + 1
    y = [[] for i in range(n_cluster)]
    for i, v in enumerate(labels):
        y[v].append(i)
    after_time = time.time()
    with open(gl.ORIGNIL_SAMPLE_PATH + 'data\\birch.json', 'w') as fp:
        json.dump({'labels': y, 'time': after_time - before_time}, fp)
    print('Finish the Birch cluster,\n And the Time cost is {}'.\
    format(after_time - before_time))
    X.close()

def set_Tsne():
    sample_path = gl.ORIGNIL_SAMPLE_PATH + 'data\\orignal_sample.hdf5'
    batch_path = gl.ORIGNIL_SAMPLE_PATH + 'data\\batch_sample.hdf5'
    shape = (gl.TIMES_STEPS, gl.FEATRUE_NUMBER)
    X = Dataset(sample_path, batch_path, st.BATCH_HDF5, gl.ORIGNIL_SAMPLE_NUM, shape)
    dis_matrix = get_dis_matrix(X, euclidean, 380)
    X_embedded = TSNE(n_components=2, metric='precomputed').fit_transform(dis_matrix)
    with open(gl.ORIGNIL_SAMPLE_PATH + 'data/tsne-euclidean.json', 'w') as fp: 
        json.dump({'pos': X_embedded.tolist()}, fp)


# cluster_test()
set_Tsne()
