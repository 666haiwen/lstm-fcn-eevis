import os
import json
import numpy as np
from utils import sampling


def _removeFileInFirstDir(targetDir):   
    if not os.path.exists(targetDir):
        return
    for file in os.listdir(targetDir):   
        targetFile = os.path.join(targetDir,  file)   
        if os.path.isfile(targetFile):   
            os.remove(targetFile)
    os.rmdir(targetDir)


def removeFileInFirstDir():
    data_lists = ['fault_mark.json', 'tensor2D_normal_*.txt']
    lista = ['bus_info.json', 'edge_info.json', 'fault_mark.json']
    module_dir = os.path.dirname(__file__) + '/../data/'
    for i in range(1, 21):
        prefix = module_dir + str(i) + '/data'
        data_prefix = os.listdir(prefix)
        for data_file in data_prefix:
            if data_file not in data_lists and data_file[:17] != 'tensor2D_normal_0':
                targetFile = os.path.join(prefix, data_file)
                if os.path.exists(targetFile):
                    os.remove(targetFile)
                _removeFileInFirstDir(targetFile)
        for fileName in lista:
            targetFile = "%s%s/%s"%(module_dir, i, fileName)
            if os.path.exists(targetFile):
                os.remove(targetFile)
        for st_id in range(186, 320):
            _removeFileInFirstDir("%s%s/ST_%s" % (module_dir, i, st_id))


def sampling_faultcenter():
    prefix = "F:/Workspace/LSTM/MLSTM-src/data"
    dstfix = "F:/Workspace/LSTM/MLSTM-src/sampleData"
    for i in range(1, 21):
        grid = prefix + '/' + str(i)
        fault_path = os.path.join(grid, 'data/fault_mark.json')
        f = open(fault_path, encoding='utf-8')
        faults = json.load(f)
        grid = dstfix + '/' + str(i)
        files = os.listdir(grid)
        res = []
        for fault in faults:
            if str(fault['sample_id']) in files:
                res.append(fault)
        # res = filter(lambda fault: str(fault['sample_id']) in files, faults)
        if not os.path.exists(grid + '/data'):
            os.makedirs(grid + '/data')
        with open(grid + '/data/fault_mark.json', 'w') as fp:
            json.dump(res, fp)



def reNormalization():
    for i in range(1, 21):
        print(i)
        infoPrefix = 'F:/Workspace/LSTM/MLSTM-src/data/' + str(i) + '/data/bus_info.json'
        f = open(infoPrefix, encoding='utf-8')
        bus_info = json.load(f)
        dataPrefix = 'F:/Workspace/LSTM/MLSTM-src/sampleData/' + str(i)
        files = os.listdir(dataPrefix)
        for fileName in files:
            if fileName == 'data':
                continue
            tmp_path = dataPrefix + '/' + fileName + '/'
            f = open(tmp_path + 'bus_distance_info.json')
            bus_distance = json.load(f)
            tensor2D = np.loadtxt(tmp_path + 'tensor2D.txt')
            for idx, bus_id in enumerate(bus_distance):
                vBase = bus_info[bus_id - 1]['vBase']
                tensor2D[:, idx] *= vBase
            np.savetxt(tmp_path + 'vBase_tensor2D.txt', tensor2D, fmt='%.6e')


def sampling_fault_mapping():
    prefix = "F:/Workspace/LSTM/MLSTM-src/sampleData"
    fault_type = set()
    fault_list = []
    for i in range(1, 21):
        grid = prefix + '/' + str(i)
        fault_path = os.path.join(grid, 'data/fault_mark.json')
        f = open(fault_path, encoding='utf-8')
        faults = json.load(f)
        for fault in faults:
            fault_type.add(fault['mark'])
            fault_list.append(fault['mark'])
    fault_type = list(fault_type)
    type_max = max(fault_type)

    fault_cnt = [{'cnt':0, 'index':i} for i in range(type_max + 1)]
    for fault in fault_list:
        fault_cnt[fault]['cnt'] += 1
    fault_cnt.sort(key=lambda fault: fault['cnt'], reverse=True)

    fault_mapping = [-1 for i in range(type_max + 1)]
    cnt = 0
    fault_list = []
    for i in range(25):
        cnt += fault_cnt[i]['cnt']
        fault_mapping[fault_cnt[i]['index']] = i
        fault_list.append(fault_cnt[i]['index'])

    sample_sets = []
    for i in range(1, 21):
        grid = prefix + '/' + str(i)
        fault_path = os.path.join(grid, 'data/fault_mark.json')
        f = open(fault_path, encoding='utf-8')
        faults = json.load(f)
        sample_sets.append({
            'typeid:': i,
            'fault': []
            })
        for fault in faults:
            if fault['mark'] in fault_list:
                sample_id = fault['sample_id']
                fault_path = grid + '/{}/bus_distance_info.json'.format(sample_id)
                f = open(fault_path, encoding='utf-8')
                fault_center = json.load(f)[0]
                sample_sets[i - 1]['fault'].append({
                    'sample_id': sample_id,
                    'fault_center': fault_center,
                    'mark': fault['mark']
                })
    with open(prefix + '/fault_mapping.json', 'w') as fp:
        json.dump(fault_mapping, fp)
    with open(prefix + '/sample_sets.json', 'w') as fp:
        json.dump(sample_sets, fp)
    # print(fault_mapping, cnt)
    # print(fault_cnt)
    return fault_mapping


def faultMark(faults, sampleId):
    for fault in faults:
        if fault['sample_id'] == sampleId:
            return fault['mark']
    return -1


def sampling_data_generate():
    prefix = "F:/Workspace/LSTM/MLSTM-src/sampleData"
    dstfix = "F:/Workspace/LSTM/MLSTM-src/sampling"
    fault_mapping = sampling_fault_mapping()
    for i in range(1, 21):
        print(i)
        grid = prefix + '/' + str(i)
        fault_path = os.path.join(grid, 'data/fault_mark.json')
        f = open(fault_path, encoding='utf-8')
        faults = json.load(f)
        tmp_path = "F:/Workspace/LSTM/MLSTM-src/data/" + str(i) + '/data/bus_degrees.json'
        f = open(tmp_path, encoding='utf-8')
        degrees = json.load(f)
        files = os.listdir(grid)

        grid = dstfix + '/' + str(i)
        if not os.path.exists(grid):
            os.makedirs(grid)
        cnt = 0
        res = []
        for fileName in files:
            if fileName == 'data':
                continue
            tmp = int(fileName)
            oldFault = faultMark(faults, tmp)
            if oldFault == -1:
                continue
            newFault = fault_mapping[oldFault]
            if newFault != -1:
                path = prefix + '/' + str(i) + '/' + fileName + '/' + 'vBase_tensor2D.txt'
                print(path)
                tmp_path = prefix + '/' + str(i) + '/' + fileName + '/' + 'bus_distance_info.json'
                f = open(tmp_path, encoding='utf-8')
                bus_distance = json.load(f)

                data = np.loadtxt(path)
                for times in range(10):
                    cnt += 1
                    res.append({
                        'sample_id': cnt, 
                        'mark': newFault
                    })
                    newData = sampling(data, degrees, bus_distance)
                    wanted_shape = (501, 95)
                    if not newData.shape == wanted_shape:
                        print('Not equal of path {}'.format(path))
                    dstPath = dstfix + '/' + str(i) + '/ST_' + str(cnt)
                    if not os.path.exists(dstPath):
                        os.makedirs(dstPath)
                    np.savetxt(dstPath + '/tensor2D.txt', newData, fmt='%.6e')
        # end of for fileName in files:
        grid = dstfix + '/' + str(i)

        if not os.path.exists(grid + '/data'):
            os.makedirs(grid + '/data')
        with open(grid + '/data/fault_mark.json', 'w') as fp: 
            json.dump(res, fp)

# sampling_faultcenter()
# reNormalization()
sampling_data_generate()
# sampling_fault_mapping()
