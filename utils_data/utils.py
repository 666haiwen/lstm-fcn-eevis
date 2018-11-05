from __future__ import absolute_import, division, print_function

import json
import logging
import os
import os.path as osp
import sys
from datetime import datetime
from glob import glob
from time import localtime, strftime, time
import numpy as np
from tensorly.decomposition import parafac, tucker
sys.path.append(os.getcwd())
import utils_data.const as st
from utils_data.entropy import cal_entropy
import data_parse.const as gl


class MyFormatter(logging.Formatter):
    converter = datetime.fromtimestamp

    # Here the `record` is a LogRecord obejct
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s.%03d" % (t, record.msecs)
        return s

def create_logger(log_file=None, ternimal=True, outfile=True):
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    #formatter = logging.Formatter("%(message)s")
    formatter = MyFormatter("%(asctime)s: %(levelname).1s %(message)s")

    # Create file handler
    if outfile:
        if log_file is None:
            log_name = strftime('%Y%m%d%H%M%S', localtime(time())) + '.log'
            log_file = os.path.join(save_path, log_name)

        if os.path.exists(log_file):
            os.remove(log_file)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Create console handler
    if ternimal:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def sampling(_data):
    """Sampling data

    Params
    ------
    _data : np.ndarray with data from "tensor2D.txt"
    sampling_rate : sampling rate of data

    Returns
    -------
    data : np.ndarray after sampling
    """
    if st.SAMPLE_RATE == 1.0:
        return _data
    data = _data.copy()
    node_numbers = data.shape[1]
    delete_shape = node_numbers - int(node_numbers * st.SAMPLE_RATE)
    entropy, threshold = cal_entropy(data)
    short_node = set(filter(lambda index: entropy[index] < threshold and index > 1, range(node_numbers)))
    # len of short_node is uncertain since threshold value may not unique
    delete_shape -= len(short_node)
    remaning_node = list(set([i for i in range(node_numbers)]) - short_node)
    remaning_size = len(remaning_node)
    delete_sampling = set()
    while len(delete_sampling) < delete_shape:
        delete_sampling.add(remaning_node[np.random.randint(2, remaning_size)])

    # id_and_degree = np.zeros(shape=(2, node_numbers))
    # for i in range(node_numbers):
    #     id_and_degree[0][i] = bus_distance[i]
    #     id_and_degree[1][i] = degrees[bus_distance[i]]

    # sampling with zero filling
    # zero_node = np.zeros(shape=(data.shape[0]))
    # for i in delete_node:
    #     data[:, i] = zero_node
    # return data

    # sampling without zero filling
    delete_node = list(delete_sampling | short_node)
    delete_data = np.delete(data, delete_node, 1)
    # delete_bus = np.delete(id_and_degree, delete_node, 1)
    return delete_data
    # return np.concatenate((delete_bus, delete_data), axis=0)


def decomposition(tensor, dfunc='cp', rank=3, ranks=[2, 3, 2]):
    """tensor decompostion using tensorly

    Params
    ------
    tensor : np.ndarray with data from "tensor2D.txt"
    dfunc : cp or tucker
    rank: cp-rank
    ranks: tucker-core

    Returns
    -------
    factors : np.ndarray after tensor decompostion, shape=(2,)
    core: np.ndarray after tensor decomposition, shape=ranks.shape
    """
    if dfunc == 'cp':
    ## CP-Decomposition
        factors = parafac(tensor, rank=rank, init='svd')
        return factors
    ## Tucker-decomposition
    if dfunc == 'tucker':
        core, factors = tucker(tensor, ranks=ranks)
        return core, factors


def gauss_normalization(_data):
    """ Normaliztion a matrix into Standard normal distribution

    Params
    ------
    _data: np.ndarray, ndim=2

    Returns
    -------
    data: np.ndarray, ndim=2
    """
    data = np.copy(_data)
    shape = data.shape
    for j in range(shape[1]):
        mean = np.mean(data[:, j])
        std = np.std(data[:, j], ddof=1)
        data[:, j] = (data[:, j] - mean) / std
    return data


def sax(tensor):
    """  Symbolic Aggregate approXimation for time series data just like cols in tensor data
         Translate time series data into Alphabet by PAA --> Normaliztion --> Discretization

    Params
    ------
    tensor : np.ndarray with data from "tensor2D.txt"

    Returns
    -------
    data : Alphabet data after sax, shape=(w, feature_number), type=list

    Reference
    ---------
    Paper A Symbolic Representation of Time Series, with Implications for Streaming Algorithms
    Link: http://www.cs.ucr.edu/~eamonn/SAX.pdf
    """
    shape = tensor.shape
    if shape[0] != gl.TIMES_STEPS:
        raise ValueError('Time Steps in tensor must be {}'.format(gl.TIMES_STEPS))
    if shape[1] != st.SAMPLE_FETURE:
        raise ValueError('Feature Number in tensor must be {}'.format(st.SAMPLE_FETURE))
    
    paa = np.zeros((st.PAA_W, st.SAMPLE_FETURE))
    rate = st.PAA_RATE
    for j in range(st.SAMPLE_FETURE):
        for i in range(st.PAA_W):
            paa[i][j] = np.sum(tensor[i*rate:((i + 1)*rate - 1), j]) / rate
    paa = gauss_normalization(paa)

    data = [[st.SYMBOLS[st.BREAK_A - 1] for j in range(st.SAMPLE_FETURE)] for i in range(st.PAA_W)]
    for j in range(st.SAMPLE_FETURE):
        for i in range(st.PAA_W):
            for k in range(st.BREAK_A - 1):
                if paa[i][j] < st.BREAK_POINTS[k]:
                    data[i][j] = st.SYMBOLS[k]
                    break
    return data


def mindis(Q, C):
    """ calculate MINDIST between symbol matrix Q and C

    Params
    ------
    Q, C: symbol matrix to calculate

    Return
    ------
    D: distance vector between Q and C
    """
    D = np.zeros((st.SAMPLE_FETURE))
    for i in range(st.SAMPLE_FETURE):
        q = [x[i] for x in Q]
        c = [x[i] for x in C]
        length = len(q)
        for j in range(length):
            D[i] += st.DIST_TABLE[st.INDEX_S[q[j]]][st.INDEX_S[c[j]]] ** 2
        D[i] = np.sqrt(st.PAA_RATE * D[i])
    return D


def dis(Q, C):
    """ calculate Euclidean distance between tensor Q and C

    Params
    ------
    Q, C: tensor dataz

    Return
    ------
    D: distance vector between Q and C
    """
    D = np.zeros((st.SAMPLE_FETURE))
    for i in range(st.SAMPLE_FETURE):
        D[i] = np.sqrt(np.sum((Q[:,i] - C[:,i]) ** 2))
    return D, np.sum(D)


def test_transfer_eff(tensor):
    res = np.zeros((5 * st.BREAK_A, st.SAMPLE_FETURE))
    for j in range(st.SAMPLE_FETURE):
        mean = np.mean(tensor[:, j])
        std = np.std(tensor[:, j], ddof=1)
        org_gauss = [x * std + mean for x in st.BREAK_POINTS]
        tmp_list = [[] for i in range(st.BREAK_A)]
        for x in tensor[:,j]:
            index = st.BREAK_A - 1
            for k in range(st.BREAK_A - 1):
                if x < org_gauss[k]:
                    index = k
                    break
            tmp_list[index].append(x)
        for i in range(st.BREAK_A):
            sorted(tmp_list[i])
            length = len(tmp_list[i])
            if length == 0:
                continue
            tmp_array = np.array(tmp_list[i])
            res[i * 5, j] = np.mean(tmp_array)
            res[i * 5 + 1, j] = np.std(tmp_array)
            res[i * 5 + 2, j] = tmp_array[int(length / 2)]
            res[i * 5 + 3, j] = tmp_array[int(length / 4)]
            res[i * 5 + 4, j] = length
    return res


def dtw(x, y):
    """calculate 1*D array x and y distance by dtw

    Args:
        x,y 1*D array of input to dtw

    Returns:
        vaule after dtw
    """
    d = np.array([[abs(i - j) for j in y] for i in x])
    len_x = len(x)
    len_y = len(y)
    g = np.zeros((len_x, len_y), dtype=np.float)
    g[0][0] = d[0][0]
    for i in range(1, len_x):
        g[i][0] = g[i - 1][0] + d[i][0]
    for j in range(1, len_y):
        g[0][j] = g[0][j - 1] + d[0][j]
    for i in range(1, len_x):
        for j in range(1, len_y):
            g[i][j] = d[i][j] + min(g[i - 1][j - 1], g[i - 1][j], g[i][j - 1])
    return g[len_x - 1][len_y - 1]


def get_sm(_data, d_type, dis_type='euclid'):
    """get similar matrix from _data

    """
    if d_type == 'symbol':
        shape = (st.PAA_W, st.SAMPLE_FETURE)
        data = _data
        sm = np.zeros((shape[1], shape[1]), )
    else:
        if d_type == 'paa':
            tensor = gauss_normalization(_data)
            data = np.ones((st.PAA_W, st.SAMPLE_FETURE))
            rate = int(gl.TIMES_STEPS / st.PAA_W)
            for j in range(st.SAMPLE_FETURE):
                for i in range(st.PAA_W):
                    data[i][j] = np.sum(tensor[i*rate:((i + 1)*rate - 1), j]) / rate
        elif d_type == 'tensor':
            data = _data

        shape = data.shape
        sm = np.ones((shape[1], shape[1]), )

    for col in range(shape[1]):
        for pre in range(col):
            if d_type == 'symbol':
                for j in range(shape[0]):
                    sm[col][pre] += st.DIST_TABLE[st.INDEX_S[data[j][col]]][st.INDEX_S[data[j][pre]]] ** 2
                sm[col][pre] = np.sqrt(st.PAA_RATE * sm[col][pre])
            elif d_type == 'tensor':
                if dis_type == 'euclid':
                    sm[col][pre] = np.sqrt(np.sum((data[:, col] - data[:, pre]) ** 2))
                    if sm[col][pre] == 0:
                        sm[col][pre] = 1
                elif dis_type == 'dtw':
                    sm[col][pre] = dtw(data[:, col], data[:, pre])
            elif d_type == 'paa':
                sm[col][pre] = np.sqrt(st.PAA_RATE * (np.sum((data[:, col] - data[:, pre]) ** 2)))
                if sm[col][pre] == 0:
                        sm[col][pre] = 1
    return sm


def read_one_case(path, verbose=False, flatten=False):
    """ Get one input case

    Params
    ------
    path : path to the txt file "tensor2D.txt"
    verbose : display data size or not
    flatten : resize data into one-dimensional or not
    sampling_rate : sampling rate of data

    Returns
    -------
    data : np.ndarray with the same shape of the source data in the text file
    """

    # data = sampling(np.loadtxt(path))
    data = np.loadtxt(path)
    shape = data.shape    
    if verbose:
        print("size:", data.shape)
    if flatten:
        return data.reshape(shape[0] * shape[1])
    return data


def read_a_set_labels(path, verbose=False):
    """ Get a set of labels which contain ~176 cases

    Params
    ------
    path : path to the json file "fault_mark.json"
    verbose : display data size or not

    Returns
    -------
    data : a dict whose (key, value) pairs represent (case number: ST_x, label: 0~3)
    """

    with open(path) as f:
        data = f.read()

    labels_list = json.loads(data)
    labels = {}
    for label in labels_list:
        labels["ST_{}".format(label['sample_id'])] = label['mark']

    if verbose:
        print("size:", len(labels_list))

    return labels


def analysis_data(data_root, output=None):
    import sys
    sys.path.append(osp.join(osp.dirname(__file__), ".."))
    from config import cfg

    if not osp.isdir(data_root):
        raise FileNotFoundError("Can not find directory `%s`" % data_root)
    
    if output is not None:
        logger = create_logger(output)
    else:
        logger = create_logger(outfile=False)

    grids_list = glob(osp.join(data_root, "*"))
    logger.info("Number of grids: {}".format(len(grids_list)))

    ST_list = glob(osp.join(grids_list[0], "ST_*"))
    one_case = read_one_case(osp.join(ST_list[0], cfg.DATA.OBJ_FILE))

    ST_counter = 0
    for grid in grids_list:
        ST_list = glob(osp.join(grid, "ST_*"))
        ST_counter += len(ST_list)
    
    logger.info("Total number of ST: {}".format(ST_counter))
    logger.info("Shape of the first case: " + str(one_case.shape))

    res = input("Check raw data shape?(Y/[N])")
    check = False
    if res.lower() in ('y', 'yes'):
        check = True
    
    dst_shape = one_case.shape
    fake_counter = 0
    
    logger.info("Checking raw data...")
    for grid in grids_list:
        # check real cases
        ST_list = glob(osp.join(grid, "ST_*"))
        for ST in ST_list:
            ph = osp.join(ST, cfg.DATA.OBJ_FILE)
            if not osp.exists(ph):
                logger.error("Not found: " + ph)
                continue
            if check:
                new_case = read_one_case(ph)
                if dst_shape != new_case.shape:
                    logger.error("Mismatch: " + ph)
                del new_case
        # check fake cases
        FAKE_list = glob(osp.join(grid, cfg.DATA.FAKE_FILE))
        fake_counter += len(FAKE_list)
        for FAKE in FAKE_list:
            if check:
                new_case = read_one_case(FAKE)
                if dst_shape != new_case.shape:
                    logger.error("Mismatch: " + ph)
                del new_case    
    logger.info("Check raw data finished!")

    all_labels = []
    logger.info("Checking labels...")
    for grid in grids_list:
        labels = read_a_set_labels(osp.join(grid, cfg.DATA.LAB_FILE))
        ST_list = glob(osp.join(grid, "ST_*"))
        #logger.info("Grid {} -> {} cases...".format(osp.basename(grid), len(ST_list)))
        for ST in ST_list:
            if not osp.basename(ST) in labels.keys():
                logger.error("Miss label: " + ST)
            else:
                all_labels.append(labels[osp.basename(ST)])
    logger.info("Check labels finished!")

    logger.info("Number of classes: {}".format(1 + len(np.lib.arraysetops.unique(all_labels))))
    logger.info("Number of cases in each class: {}".format(np.concatenate((np.bincount(all_labels), [fake_counter]))))

    logger.info("Analysis finished!")

if __name__ == '__main__':
    test_path = gl.ORIGNIL_SAMPLE_PATH + 'ST_2/tensor2D.txt'
    sampling(read_one_case(test_path))
    if False:
        read_one_case(test_path, True)

    if False:
        read_a_set_labels(gl.ORIGNIL_SAMPLE_PATH + 'data/fault_mark.json', True)

    if True:
        analysis_data(gl.ORIGNIL_SAMPLE_PATH, output="./analysis-data.log")
