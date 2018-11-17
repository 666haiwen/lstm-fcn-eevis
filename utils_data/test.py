import time
import h5py
import matplotlib.pyplot as plt
import os.path as osp, os
import numpy as np
import tensorflow as tf
from utils import dis, test_transfer_eff, sax, get_sm
from const import PAA_W, PAA_RATE, BATCH_HDF5
from distance import euclidean, tf_euclidean
from data_parse import const as gl
from data_parse.utils import get_json_file

os.environ['CUDA_VISIBLE_DEVICES'] = '0'
def compare_distance():
    file1 = gl.ORIGNIL_SAMPLE_PATH + 'ST_1/'
    file2 = gl.ORIGNIL_SAMPLE_PATH + 'ST_4/'

    file1 = gl.TENSOR_SAMPLE_PATH + 'ST_101/'
    file2 = gl.TENSOR_SAMPLE_PATH + 'ST_102/'
    Q = np.loadtxt(file1 + 'tensor2D.txt')
    C = np.loadtxt(file2 + 'tensor2D.txt')
    _, res = dis(Q, C)
    print(_, res)


def test_eff():
    file1 = gl.TENSOR_SAMPLE_PATH + 'ST_101/'
    tensor = np.loadtxt(file1 + 'tensor2D.txt')
    res = test_transfer_eff(tensor)
    np.savetxt(file1 + 'eff_200_10.txt', res, fmt='%.6f')


def test_sm():
    print('PAA_BIN_WIDTH = {}, PAA_W = {}'.format(PAA_RATE, PAA_W))
    name_st = ['ST_100/', 'ST_101/', 'ST_1000/', 'ST_1001/','ST_10000/', 'ST_10001/']
    for name in name_st:
        file1 = gl.TENSOR_SAMPLE_PATH + name
        tensor = np.loadtxt(file1 + 'tensor2D.txt')
        tensor_sm = get_sm(tensor, d_type='tensor', dis_type='euclid')
        paa_sm = get_sm(tensor, d_type='paa', dis_type='euclid')

        symbol = sax(tensor)
        symbol_sm = get_sm(symbol, d_type='symbol')
        res_symbol = np.sum(np.abs(symbol_sm / paa_sm)) / 475 / 474 * 2
        res_orig = np.sum(np.abs(paa_sm / tensor_sm)) / 475 / 474 * 2
        print('Dived of symbol / paa {} is : {}'.format(name, res_symbol))
        print('Dived of paa / tensor {} is : {}'.format(name, res_orig))


def test_data():
    path = gl.DST_PATH
    res1 = get_json_file(path + 'ST_1\\', 'voltages.json')
    res2 = get_json_file(path + 'ST_5\\', 'voltages.json')
    length = len(res1)
    dis = np.zeros(length)
    index_1 = [-1 for i in range(10000)]
    index_2 = [-1 for i in range(10000)]
    for i, v in enumerate(res1):
        index_1[v['busId']] = i
    for i, v in enumerate(res2):
        index_2[v['busId']] = i
    path = gl.ORIGNIL_SAMPLE_PATH
    bus_1 = get_json_file(path + 'ST_1\\', 'bus_distance.json')
    bus_2 = get_json_file(path + 'ST_3\\', 'bus_distance.json')
    tensor1 = np.zeros((gl.TIMES_STEPS, gl.FEATRUE_NUMBER))
    tensor2 = np.zeros((gl.TIMES_STEPS, gl.FEATRUE_NUMBER))
    for i, busId in enumerate(bus_1):
        for row, v in enumerate(res1[index_1[busId]]['data']):
            tensor1[row][i] = v
    for i, busId in enumerate(bus_2):
        for row, v in enumerate(res2[index_2[busId]]['data']):
            tensor2[row][i] = v
    print('aaa')

    
def test_distance_cost():
    file1 = gl.ORIGNIL_SAMPLE_PATH + 'ST_101/'
    file2 = gl.ORIGNIL_SAMPLE_PATH + 'ST_102/'
    Q = np.loadtxt(file1 + 'tensor2D.txt')
    C = np.loadtxt(file2 + 'tensor2D.txt')
    # for i in range(10):
    #     a = euclidean(Q, C, resType='value')
    # time_b = time.time()
    # print((time_b - time_a)/10)
    # time_a = time.time()
    # print(a)    

    sess = tf.Session()
    time_a = time.time()
    v = tf_euclidean(Q, C)
    sess.run(tf.global_variables_initializer())
    # for i in range(10):
    a = sess.run(v)
    time_b = time.time()
    print((time_b - time_a))
    print(a)    



def test_tf():
    sess = tf.Session(config=tf.ConfigProto(log_device_placement=True))
    with tf.device('/gpu:0') as target:
        pass
    a = np.array([[1,2,3],[4,5,6]])
    b = np.transpose(a)
    c = tf.matmul(a, b)
    print(a)
    print(tf.Session)


def test_hdf5():
    X = h5py.File(gl.ORIGNIL_SAMPLE_PATH + 'data\\batch_sample.hdf5', 'r+')
    Y = h5py.File(gl.ORIGNIL_SAMPLE_PATH + 'data\\orignal_sample.hdf5', 'r+')
    namelist = ['batch_' + str(i) for i in range(5)]
    a = np.zeros((BATCH_HDF5, gl.TIMES_STEPS, gl.FEATRUE_NUMBER))
    time1 = time.time()
    for i in namelist:
        print(i)
        X[i].read_direct(a)
    time2 = time.time()
    print('time of batch is {}'.format(time2-time1))
    b = np.zeros((gl.TIMES_STEPS, gl.FEATRUE_NUMBER))
    namelist = ['ST_' + str(i) for i in range(2671)]
    time1 = time.time()
    for i in namelist:
        Y[i].read_direct(b)
    time2 = time.time()
    print('time of sample is {}'.format(time2-time1))


# compare_distance()
# test_eff()
# test_sm()
# test_data()
# a = np.array([5] * 20)
# print(a)
# t = [i for i in range(20)]
# v = [max(np.exp(-i/2), 10e-5)/(np.sqrt(i + 9)) for i in t]
# print(v)
# print(10e-5/np.sqrt(1000))
# plt.scatter(t, v)
# # plt.show()

test_distance_cost()
# a = tf.Variable(tf.zeros([3,3]))
# a[:,0:2].assign(1)
# sess = tf.Session()
# sess.run(tf.global_variables_initializer())
# print(sess.run(a))
# test_tf_gpu_cpu()
# test_hdf5()
# test_tf()

# with tf.device('/gpu:0'):
#         a = tf.constant([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0,1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0], shape=[6, 9], name='a')
#         b = tf.constant([2.0, 3.0, 4.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0,1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0], shape=[6, 9], name='b')
#         c = tf.subtract(b, a)
#     # Creates a session with log_device_placement set to True.
# sess1 = tf.Session(config=tf.ConfigProto(log_device_placement=True))
# print(sess1.run(c))
# from numba import jit

# @jit(nopython=True)
# def f(x, y):
#     # A somewhat trivial example
#     return x + y

# a = np.array([1,2,3,4])
# print(f(a,a))
