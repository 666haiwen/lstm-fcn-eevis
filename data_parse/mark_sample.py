"""
    Copyright 2018-2019 VAG (Visual Analytics Group), Zhejiang Univ.

    Generate fault_mark.json and tensor2D.txt into orignial_sample
    The result is used for sampling
"""
import os
import json
import numpy as np
import sys
sys.path.append(os.path.join(os.getcwd()))
import data_parse.const as gl
import data_parse.utils as utils


def get_mark_from_tensor2D(num):
    fault_list = [{'i': 0, 'j': 0}]
    mark = [{'sample_id': 0, 'mark': 0}]
    for i in range(1, num):
        path = gl.ORIGNIL_SAMPLE_PATH + 'ST_{}/'.format(i)
        bus_distance = utils.get_json_file(path, 'bus_distance.json')
        fault = {'i': bus_distance[0], 'j': bus_distance[1]}
        current_mark = len(fault_list)
        flag = True
        for _i, fault_mark in enumerate(fault_list):
            if (fault['i'] == fault_mark['i'] and fault['j'] == fault_mark['j'])\
            or (fault['i'] == fault_mark['j'] and fault['j'] == fault_mark['i']):
                # mark has repeated
                flag = False
                current_mark = _i
                break
        # set mark
        mark.append({
            'sample_id': i,
            'mark': current_mark
        })
        if flag:
            fault_list.append({
                'i': fault['i'],
                'j': fault['j']
            })
    with open(gl.ORIGNIL_SAMPLE_PATH + 'data\\fault_mark.json', 'w') as fp:
        json.dump(mark, fp)
    with open(gl.ORIGNIL_SAMPLE_PATH + 'data\\fault_list.json', 'w') as fp:
        json.dump({
            'fault_list': fault_list,
            'last_fault_index': 5468
        }, fp)


def _adjust_original():
    """
        Adjust_original_sampling since of parts of sample has problem.
        The fault center of sample doesn't have value.
        We should remove these samples and adjust sample_id and mark_id
    """
    last_res = utils.get_json_file(gl.ORIGNIL_SAMPLE_PATH + 'data\\',\
    'fault_list.json', defaultRes={
        'fault_list':[{
            'i':0,
            'j':0
        }],
        'last_fault_index': 0
    })
    fault_list = last_res['fault_list']
    new_fault_list = [{'i':0, 'j':0}]
    mark = utils.get_json_file(gl.ORIGNIL_SAMPLE_PATH + 'data\\', 'fault_mark.json', defaultRes=[])
    new_mark = []
    index = 0
    for sample_mark in mark:
        path = gl.ORIGNIL_SAMPLE_PATH + 'ST_{}/'.format(sample_mark['sample_id'])
        if not os.path.exists(path):
            break
        reorientation = utils.get_json_file(path, 'reorientation.json')['data_st'][3:]
        if reorientation in gl.WRONG_SAMPLE_ID:
            # for file_name in os.listdir(path):
            #     os.remove(path + file_name)
            # os.rmdir(path)
            print('remove {} and {}'.format(reorientation, path))
        else:
            index += 1
            fault = fault_list[sample_mark['mark']]
            flag = True
            current_mark = len(new_fault_list)
            for i, fault_mark in enumerate(new_fault_list):
                if (fault['i'] == fault_mark['i'] and fault['j'] == fault_mark['j'])\
                or (fault['i'] == fault_mark['j'] and fault['j'] == fault_mark['i']):
                    # mark has repeated
                    flag = False
                    current_mark = i
                    break
            # set mark
            new_mark.append({
                'sample_id': index,
                'mark': current_mark
            })
            if flag:
                new_fault_list.append({
                    'i': fault['i'],
                    'j': fault['j']
                })
            # rename files
            if index == sample_mark['sample_id']:
                continue
            new_file_name = gl.ORIGNIL_SAMPLE_PATH + 'ST_' + str(index) + '/'
            if os.path.exists(new_file_name):
                print('There are some wrong with file delete when old_st: {}, new_st: {}'.format(sample_mark['sample_id'], index))
                return
            os.rename(path, new_file_name)
    # end of for sample_mark in mark

    with open(gl.ORIGNIL_SAMPLE_PATH + 'data\\new_fault_mark.json', 'w') as fp:
        json.dump(new_mark, fp)
    with open(gl.ORIGNIL_SAMPLE_PATH + 'data\\new_fault_list.json', 'w') as fp:
        json.dump({
            'fault_list': new_fault_list,
            'last_fault_index': 5477
        }, fp)


def vertify_sample(num):
    faults = utils.get_json_file(gl.DST_PATH + 'data\\', 'fault.json')
    fault_list = utils.get_json_file(gl.ORIGNIL_SAMPLE_PATH + 'data\\',\
    'fault_list.json', defaultRes={
        'fault_list':[{
            'i':0,
            'j':0
        }],
        'last_fault_index': 0
    })['fault_list']
    mark = utils.get_json_file(gl.ORIGNIL_SAMPLE_PATH + 'data\\', 'fault_mark.json', defaultRes=[])
    for i in range(1, num):
        path = gl.ORIGNIL_SAMPLE_PATH + 'ST_{}/'.format(i)
        reorientation = int(utils.get_json_file(path, 'reorientation.json')['data_st'][3:])
        bus_distance = utils.get_json_file(path, 'bus_distance.json')
        fault = faults[reorientation - 1]
        if not ((bus_distance[0] == fault['i'] and bus_distance[1] == fault['j'])\
        or (bus_distance[1] == fault['i'] and bus_distance[0] == fault['j'])):
            print('reoritation wrong of ST_{}'.format(i))
        sample_mark = mark[i]['mark']
        orignal_fault = fault_list[sample_mark]
        if not ((orignal_fault['i'] == fault['i'] and orignal_fault['j'] == fault['j'])\
        or (orignal_fault['j'] == fault['i'] and orignal_fault['i'] == fault['j'])):
            print('fault_list and fault_mark wrong of ST_{}'.format(i))


def _mark_sample(faults):
    last_res = utils.get_json_file(gl.ORIGNIL_SAMPLE_PATH + 'data\\',\
    '_fault_list.json', defaultRes={
        'fault_list':[{
            'i':0,
            'j':0
        }],
        'last_fault_index': 0
    })
    fault_list = last_res['fault_list']
    last_fault_index = last_res['last_fault_index']
    mark = utils.get_json_file(gl.ORIGNIL_SAMPLE_PATH + 'data\\', '_fault_mark.json', defaultRes=[])
    # sample id
    index = 0
    for fault_index, fault in enumerate(faults):
        if fault_index >= 5:
            break
        if fault_index < last_fault_index or fault['st'] in gl.WRONG_SAMPLE_ID:
            continue
        if fault['type'] == gl.FAULT_TYPE:
            path = gl.DST_PATH + '\\ST_' + fault['st'] + '\\'
            # get shortest path
            shortest_path = utils.get_json_file(path, 'shortest_path.json')['busIds']
            # get voltage of specific sample
            voltages = utils.get_json_file(path, 'voltages.json')
            voltage_index = [-1 for i in range(gl.BUS_NUMBER + 1)]
            for i, voltage in enumerate(voltages):
                voltage_index[voltage['busId']] = i

            # faulter center does't have value or value are zeor should be filtered
            if voltage_index[fault['i']] == -1 or voltage_index[fault['j']] == -1\
            or fault['i'] in gl.UNLESS_BUS_ID or fault['j'] in gl.UNLESS_BUS_ID:
                continue

            # get tensor
            tensor = np.zeros((gl.TIMES_STEPS, gl.FEATRUE_NUMBER), dtype=np.float)
            bus_distance = []
            y = -1
            index += 1
            for busId in shortest_path:
                if voltage_index[busId] == -1 or busId == 0 or busId in gl.UNLESS_BUS_ID:
                    continue
                bus_distance.append(busId)
                y += 1
                if y > gl.FEATRUE_NUMBER:
                    print('Feature number more then {} in ST_{}'.format(gl.FEATRUE_NUMBER, fault['st']))
                    break
                for x, v in enumerate(voltages[voltage_index[busId]]['data']):
                    tensor[x][y] = v
                if np.max(tensor[:, y]) == 0:
                    print('The busId is {} which is filled with zero'.format(busId))
            if y < gl.FEATRUE_NUMBER - 1:
                print('Feature number is {} less then {} in ST_{}'.format(y, gl.FEATRUE_NUMBER, fault['st']))

            # save tensro
            path = gl.ORIGNIL_SAMPLE_PATH + 'ST_' + str(index) + '\\'
            if not os.path.exists(path):
                os.makedirs(path)
            print('Saveing tensor2D to {} From fault_index of {}'.format(path, fault_index))
            np.savetxt(path + '_tensor2D.txt', tensor, fmt='%.6e')
            # set bus_distance of tensor2D
            with open(path + '_bus_distance.json', 'w') as fp:
                json.dump(bus_distance, fp)
            # set reorientation of original_sample to data
            path = gl.ORIGNIL_SAMPLE_PATH + 'ST_' + str(index) + '\\'
            with open(path + '_reorientation.json', 'w') as fp:
                json.dump({'data_st': 'ST_' + fault['st']}, fp)


            # get mark
            current_mark = len(fault_list)
            flag = True
            for i, fault_mark in enumerate(fault_list):
                if (fault['i'] == fault_mark['i'] and fault['j'] == fault_mark['j'])\
                or (fault['i'] == fault_mark['j'] and fault['j'] == fault_mark['i']):
                    # mark has repeated
                    flag = False
                    current_mark = i
                    break
            # set mark
            mark.append({
                'sample_id': index,
                'mark': current_mark
            })
            if flag:
                fault_list.append({
                    'i': fault['i'],
                    'j': fault['j']
                })
            # temporary save just in case of program stopping unexpected
            print('Saving temporary fault_mark and fault_list of index: ' + str(fault_index))
            with open(gl.ORIGNIL_SAMPLE_PATH + 'data\\_fault_mark.json', 'w') as fp:
                json.dump(mark, fp)
            with open(gl.ORIGNIL_SAMPLE_PATH + 'data\\_fault_list.json', 'w') as fp:
                json.dump({
                    'fault_list': fault_list,
                    'last_fault_index': fault_index
                }, fp)


def mark_sample():
    faults = utils.get_json_file(gl.DST_PATH + 'data\\', 'fault.json')
    _mark_sample(faults)


if __name__ == '__main__':
    # get_mark_from_tensor2D(gl.ORIGNIL_SAMPLE_NUM)
    mark_sample()
    # vertify_sample(gl.ORIGNIL_SAMPLE_NUM)
    # _adjust_original()
