"""
    Copyright 2018-2019 VAG (Visual Analytics Group), Zhejiang Univ.

    Generate edge_info.json from LF.Lx where x from 2 to end
"""
import json
import os
import math
# application-specific imports
import sys
sys.path.append(os.path.join(os.getcwd()))
from data_parse.const import FILE_PATH, DST_PATH


# electrical distance = sqrt(r*r + x*x)
# r:电阻 x:电抗
def _edge_info(file_path):
    prefix = file_path
    edges = []
    with open(prefix + 'LF.L2', 'r', encoding='gbk') as fp:
        for line in fp:
            line = list(filter(lambda str : len(str) != 0,
                [x.strip('\' ') for x in line.split(',')]))
            if line[0] == '0':
                continue
            i = int(line[1])
            j = int(line[2])
            if i != j:
                # line[4]: 线路正序电阻
                r = float(line[4])
                # line[5]: 线路正序电抗
                x = float(line[5])
                edges.append({
                    'i': i,
                    'j': j,
                    'dis': math.sqrt(r * r + x * x),
                    'ID_Name': line[-2]
                })
    with open(prefix + 'LF.L3', 'r', encoding='gbk') as fp:
        for line in fp:
            line = list(filter(lambda str : len(str) != 0,
                [x.strip('\' ') for x in line.split(',')]))
            if line[0] == '0':
                continue
            # line[4]: 线路正序电阻
            r = float(line[4])
            # line[5]: 线路正序电抗
            x = float(line[5])
            edges.append({
                'i': abs(int(line[1])),
                'j': int(line[2]),
                'dis': math.sqrt(r * r + x * x),
                'ID_Name': line[-2]
            })
    # Install to ../data/data/
    path_prefix = DST_PATH + 'data\\'
    print('Writing edge_info.json to: ' + path_prefix + ' ...')
    # Create directory if not exist
    if not os.path.exists(path_prefix):
        os.makedirs(path_prefix)
    # Write file to that directory
    with open(path_prefix + 'edge_info.json', 'w', encoding='utf-8') as fp:
        json.dump(edges, fp, ensure_ascii=False)



def edge_info():
    _edge_info(FILE_PATH)


if __name__ == '__main__':
    edge_info()
