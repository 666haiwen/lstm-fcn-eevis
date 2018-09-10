"""
    Copyright 2018-2019 VAG (Visual Analytics Group), Zhejiang Univ.

    Generate fault.json for each sample
    And msg got from file's Name
"""
import json
# src
import sys
import os
sys.path.append(os.path.join(os.getcwd()))
import data_parse.utils as utils
from data_parse.const import DST_PATH


def _fault_mark(fileName, st):
    fault_msg = fileName.split('_')
    fault_i = fault_msg[0].strip('E')
    fault_j = fault_msg[1]
    fault_type = fault_msg[-1]
    return {
        'i': int(fault_i),
        'j': int(fault_j),
        'type': fault_type,
        'st': st
    }


def fault_mark():
    """Export this function for install.py"""
    files = utils.get_file_list()
    fault_list = []
    for i, fileName in enumerate(files):
        fault_list.append(_fault_mark(fileName, str(i + 1)))
    dstfix = DST_PATH + 'data\\'
    print('Writing fault.json to: ' + dstfix + ' ...')
    with open(dstfix + 'fault.json', 'w') as fp:
        json.dump(fault_list, fp)


if __name__ == '__main__':
    fault_mark()
