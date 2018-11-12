import numpy as np
import math
from utils import dis, test_transfer_eff, sax, get_sm
from const import PAA_W, PAA_RATE
from data_parse import const as gl
from data_parse.utils import get_json_file


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

    
# compare_distance()
# test_eff()
# test_sm()
test_data()
# a = np.array([1.25,2.85,3.6,4.1,5.0])
# b = np.copy

# a = np.exp(complex(0,1))
# print(a)
# b = complex(2,1)
# print(a + b)
# print(a * b)