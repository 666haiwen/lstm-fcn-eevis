import math
import sys
import json
import os
import matplotlib.pyplot as plt
import numpy as np
sys.path.append(os.getcwd())
import utils_data.const as gl
import data_parse.const as test


def get_range(data):
    v_max = v_min = data[0][0]
    size = data.shape
    for col in range(0, size[1]):
        v_max = max(v_max, max(data[:, col]))
        v_min = min(v_min, min(data[:, col]))
    return v_max, v_min


def entropy_draw(entropy):
    entropy.sort()
    size = len(entropy)
    tmp = size // 4
    print(entropy[tmp - 1], entropy[tmp * 2 - 1], entropy[tmp * 3 - 1], entropy[tmp * 4 - 1])

    e_min = min(entropy)
    e_max = max(entropy)
    bucket = (e_max - e_min) / gl.ENTROPY_RANGE
    entropy_his = [0 for i in range(gl.ENTROPY_RANGE)]
    for _entropy in entropy:
        entropy_id = min(gl.ENTROPY_RANGE - 1, int((_entropy - e_min) / bucket))
        entropy_his[entropy_id] += 1
    plt.figure(figsize=(10, 10))
    plt.hist(entropy, bins=40, facecolor='yellowgreen', edgecolor='b')
    plt.grid(True)
    plt.show()


def bucket_set(node, v_max, v_min):
    """ split data into interval of fixed number

    Params
    ------
    node :  ndarray(timesteps, ) of node data

    Returns
    -------
    node : after split node in ndarray
    """
    bucket = (v_max - v_min) / gl.SPLIT_RANGE
    if bucket < sys.float_info.epsilon:
        bucket = gl.SPLIT_RANGE
    node = (abs(node - v_min)) // bucket
    return node


def cal_entropy(data):
    """ calculate entropy of the data

    Params
    ------
    data : ndarray(timesteps, features) of sample

    Returns
    -------
    entropy : a list of all nodes entropy values
    """
    size = data.shape
    v_max, v_min = get_range(data)
    bucket = max((v_max - v_min) / gl.SPLIT_RANGE, sys.float_info.epsilon)

    entropy = []
    for col in range(0, size[1]):
        node = (abs(data[:, col] - v_min)) // bucket
        v_set = set(list(node))
        ent = 0.0
        for x_value in v_set:
            p = float(node[node == x_value].shape[0]) / node.shape[0]
            logp = np.log2(p)
            ent -= p * logp
        if math.isnan(ent):
            print(col)
        entropy.append(ent)
    entropy_bak = entropy.copy()
    entropy.sort()
    # entropy_draw(entropy)
    return entropy_bak, entropy[int(size[1] * (1 - gl.SAMPLE_THRESHOLD))]


def entropy_test():
    path = test.ORIGNIL_SAMPLE_PATH + 'ST_2/tensor2D.txt'
    data = np.loadtxt(path)
    entropy, threshold = cal_entropy(data)
    print(entropy, threshold)


# entropy_test()
