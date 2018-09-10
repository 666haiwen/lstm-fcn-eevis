"""
    Copyright 2018-2019 VAG (Visual Analytics Group), Zhejiang Univ.

    Generate bus_info.json from LF.L1
"""
# standard library imports
import json
import os
import sys
sys.path.append(os.path.join(os.getcwd()))
# application-specific imports
from data_parse.const import FILE_PATH, DST_PATH


def _bus_info(file_path):
    prefix = file_path
    result = []
    bus_id = 0
    with open(prefix + 'LF.L1', 'r', encoding='gbk') as fp:
        for line in fp:
            bus_id += 1
            origin = line.split(',')
            formatted = [bus_id]
            for data in origin:
                formatted.append(data.strip('\' '))
            result.append({
                'busId': int(formatted[0]),
                'busName': formatted[1],
                'vBase': float(formatted[2]),
                'area': int(formatted[3]),
                'vMax': float(formatted[4]),
                'vMin': float(formatted[5])
            })
    # Install to ../data/data/
    path_prefix = DST_PATH + 'data\\'
    print('Writing bus_info.json to: ' + path_prefix + ' ...')
    # Create directory if not exist
    if not os.path.exists(path_prefix):
        os.makedirs(path_prefix)
    # Write file to that directory
    with open(path_prefix + 'bus_info.json', 'w', encoding='utf-8') as fp:
        json.dump(result, fp, ensure_ascii=False)


def bus_info():
    """Export this function for install.py"""
    _bus_info(FILE_PATH)


if __name__ == '__main__':
    bus_info()
