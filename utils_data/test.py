import numpy as np
import math
from utils import dis, test_transfer_eff, sax, get_sm
from const import PAA_W, PAA_RATE
from data_parse import const as gl


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


# compare_distance()
# test_eff()
test_sm()
