import sys
import os
import json
import h5py
import numpy as np
sys.path.append(os.getcwd())
from utils_data.utils import sampling, sax, dis, mindis
from utils_data.const import TENSORE_FILE, TIMES_EXPANSION, SAMPLE_RATE, NO_FILLING, SAMPLE_FETURE
from data_parse.utils import get_json_file
import data_parse.const as gl


def reNormalization():
    bus_info = get_json_file(gl.DST_PATH + 'data\\', 'bus_info.json')
    for i in range(1, gl.ORIGNIL_SAMPLE_NUM + 1):
        tmp_path = gl.ORIGNIL_SAMPLE_PATH + 'ST_' + str(i) + '\\'
        reorientation = get_json_file(tmp_path, 'reorientation.json')['data_st']
        tensor2D = np.loadtxt(tmp_path + 'tensor2D.txt')
        tmp_path = gl.DST_PATH + reorientation + '\\'
        bus_distance = get_json_file(tmp_path, 'shortest_path.json')
        for idx, bus_id in enumerate(bus_distance):
            vBase = bus_info[bus_id - 1]['vBase']
            tensor2D[:, idx] *= vBase
        np.savetxt(tmp_path + 'vBase_tensor2D.txt', tensor2D, fmt='%.6e')


def sampling_data_generate():
    mark = get_json_file(gl.ORIGNIL_SAMPLE_PATH + 'data\\', 'fault_mark.json')
    sample_logs = get_json_file(gl.TENSOR_SAMPLE_PATH + 'data\\', 'sample_logs.json', {'mark_used': [], 'orignal_sample_used': []})
    mark_used = sample_logs['mark_used']
    orignal_sample_used = sample_logs['orignal_sample_used']
    cnt = len(mark_used) * TIMES_EXPANSION + TIMES_EXPANSION * gl.LABELS_NUM
    res = get_json_file(gl.TENSOR_SAMPLE_PATH + 'data\\', 'fault_mark.json', defaultRes=[])[:cnt]
    # begin to generate samples
    for sample_mark in mark:
        if sample_mark['mark'] not in mark_used:
            st_id = sample_mark['sample_id']
            mark_used.append(sample_mark['mark'])
            orignal_sample_used.append(st_id)
            file_path = gl.ORIGNIL_SAMPLE_PATH + 'ST_{}\\{}'.format(st_id, TENSORE_FILE)
            data = np.loadtxt(file_path)
            for times in range(TIMES_EXPANSION):
                cnt += 1
                res.append({
                    'sample_id': cnt,
                    'mark': sample_mark['mark']
                })
                newData = sampling(data)
                tmp_rate = 1
                if NO_FILLING == 1:
                    tmp_rate = SAMPLE_RATE
                wanted_shape = (gl.TIMES_STEPS, int(tmp_rate * gl.FEATRUE_NUMBER))
                if not newData.shape == wanted_shape:
                    print('Not equal of path {}'.format(file_path))
                # save new data
                dstPath = gl.TENSOR_SAMPLE_PATH + 'ST_{}/'.format(cnt)
                if not os.path.exists(dstPath):
                    os.makedirs(dstPath)
                np.savetxt(dstPath + 'tensor2D.txt', newData, fmt='%.6e')
            # save temporary in case of interrupt suddenly
            with open(gl.TENSOR_SAMPLE_PATH + 'data/fault_mark.json', 'w') as fp: 
                json.dump(res, fp)
            with open(gl.TENSOR_SAMPLE_PATH + 'data/sample_logs.json', 'w') as fp: 
                json.dump({'mark_used': mark_used, 'orignal_sample_used': orignal_sample_used}, fp)
    # end of for sample_mark in mark


def union_fault_mark():
    mark_a = get_json_file(gl.TENSOR_SAMPLE_PATH + 'data\\', 'fault_mark.json', defaultRes=[])
    mark_b = get_json_file(gl.TMP_SAMPLE_PATH + 'data\\', 'fault_mark.json', defaultRes=[])
    mark_a += mark_b
    with open(gl.TENSOR_SAMPLE_PATH + 'data/_fault_mark.json', 'w') as fp: 
        json.dump(mark_a, fp)


def alphabet_data_generate():
    """
        Symbolic Aggregate approXimation for time series data just like cols in tensor data
        paper: A Symbolic Representation of Time Series, with Implications for Streaming Algorithms
        link: http://www.cs.ucr.edu/~eamonn/SAX.pdf

        Translate time series data into Alphabet by PAA --> Normaliztion --> Discretization
    """
    tensor_files = os.listdir(gl.TENSOR_SAMPLE_PATH)
    # for i, file_name in enumerate(tensor_files):
    for i in range(51, 202, 50):
        file_name = 'ST_' + str(i)
        if file_name == 'data':
            continue
        file_path = gl.TENSOR_SAMPLE_PATH + file_name + '\\'
        tensor = np.loadtxt(file_path + 'tensor2D.txt')
        symbols = sax(tensor)
        length = len(symbols)
        fileObj = open(file_path + 'symbols.txt', 'w')
        for row in range(length):
            for col in range(SAMPLE_FETURE):
                fileObj.write(symbols[row][col] + ' ')
            fileObj.write('\n')
        print(file_name)
        if i == 51:
            pre_symbols = symbols
            pre_tensor = tensor
        else:
            dis_sym = mindis(pre_symbols, symbols)
            dis_org = dis(pre_tensor, tensor)
            dis_res = np.zeros((4, SAMPLE_FETURE))
            dis_res[0] = dis_sym
            dis_res[1] = dis_org
            dis_res[2] = dis_sym / dis_org
            dis_res[3][0] = np.mean(dis_sym)
            dis_res[3][1] = np.mean(dis_org)
            dis_res[3][2] = dis_res[3][0] / dis_res[3][1]
            np.savetxt(file_path + 'dis.txt', dis_res, fmt='%.6e')


# reNormalization()
# sampling_data_generate()
# union_fault_mark()
alphabet_data_generate()
