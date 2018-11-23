import json
from sklearn.manifold import TSNE
from data_parse import const as gl
from utils_data import const as st
from utils_data.cluster.numba_distance import *
from utils_data.cluster.dataset import get_dis_matrix, Dataset


def set_Tsne():
    sample_path = gl.ORIGNIL_SAMPLE_PATH + 'data\\orignal_sample.hdf5'
    batch_path = gl.ORIGNIL_SAMPLE_PATH + 'data\\batch_sample.hdf5'
    shape = (gl.TIMES_STEPS, gl.FEATRUE_NUMBER)
    X = Dataset(sample_path, batch_path, st.BATCH_HDF5, gl.ORIGNIL_SAMPLE_NUM, shape)
    dis_matrix = get_dis_matrix(X, euclidean)
    X_embedded = TSNE(n_components=2, metric='precomputed').fit_transform(dis_matrix)
    with open(gl.ORIGNIL_SAMPLE_PATH + 'data/tsne-euclidean.json', 'w') as fp: 
        json.dump({'pos': X_embedded}, fp)

set_Tsne()
