import sys
import os
import json
import h5py
import numpy as np
sys.path.append(os.getcwd())
from utils_data.utils import sampling, decomposition
from utils_data.const import TENSORE_FILE, TIMES_EXPANSION, SAMPLE_RATE, NO_FILLING, CP_RANK
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


def tensor_decomposition():
    tensor_files = os.listdir(gl.TENSOR_SAMPLE_PATH)
    for i, file_name in enumerate(tensor_files):
        if file_name == 'data':
            continue
        file_path = gl.TENSOR_SAMPLE_PATH + file_name + '\\'
        tensor = np.loadtxt(file_path + 'tensor2D.txt')
        factors = decomposition(tensor, rank=CP_RANK)
        np.savetxt(file_path + 'cp-time.txt', factors[0], fmt='%.8e')
        np.savetxt(file_path + 'cp-busId.txt', factors[1], fmt='%.8e')
        print(file_name)
        if i == 20:
            return


# reNormalization()
# sampling_data_generate()
# union_fault_mark()
tensor_decomposition()
