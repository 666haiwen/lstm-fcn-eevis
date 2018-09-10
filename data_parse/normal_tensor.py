"""
    Copyright 2018-2019 VAG (Visual Analytics Group), Zhejiang Univ.

    Generate normal sample data for training
"""
import os
import sys
import json
import numpy as np
sys.path.append(os.path.join(os.getcwd()))
import data_parse.utils as utils
import data_parse.const as gl


def _generate_normal_sample():
    template_file = gl.ORIGNIL_SAMPLE_PATH + 'ST_1/tensor2D.txt'
    _data = np.loadtxt(template_file)
    delete_node = [i for i in range(100, gl.TIMES_STEPS)]
    _data = np.delete(_data, delete_node, 0)
    tensor = np.zeros((gl.TIMES_STEPS, gl.FEATRUE_NUMBER), dtype=np.float)

    shape = tensor.shape
    std = np.std(_data, axis=0)
    bus_distance_info = utils.get_json_file(gl.ORIGNIL_SAMPLE_PATH + 'ST_1/', 'bus_distance.json')
    # bus_info = utils.get_json_file(gl.DST_PATH + 'data/', 'bus_info.json')
    index = 0
    for f in range(0, shape[1]):
        # vBase = bus_info[bus_distance_info[f] - 1]['vBase']
        # vMax = bus_info[bus_distance_info[f] - 1]['vMax']
        # vMin = bus_info[bus_distance_info[f] - 1]['vMin']
        for t in range(shape[0]):
            random_v = np.random.normal(1, std[f])
            # while (vMax != 0 and vMin != 0) and (random_v < vMin or random_v > vMax):
            #     random_v = np.random.normal(vBase, std[f])
            tensor[t][f] = random_v
    path = gl.ORIGNIL_SAMPLE_PATH + 'ST_0/'
    print('the number of wrong bus: ' + str(index))
    if not os.path.exists(path):
        os.makedirs(path)
    np.savetxt(path + 'tensor2D.txt', tensor, fmt='%.6e')
    with open(path + 'bus_distance.json', 'w') as fp: 
        json.dump(bus_distance_info, fp)


if __name__ == '__main__':
    _generate_normal_sample()
