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
from utils_data.const import SAMPLE_RATE
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
    if SAMPLE_RATE == 1.0:
        return _data
    data = _data.copy()
    node_numbers = data.shape[1]
    delete_shape = node_numbers - int(node_numbers * SAMPLE_RATE)
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
