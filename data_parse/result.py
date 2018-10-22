"""
    Copyright 2018-2019 VAG (Visual Analytics Group), Zhejiang Univ.

    Generate voltages.json and phase_angles.json by FNx.DAT and meta.py
    where x from 1 to end
"""
import json
import os
import sys
sys.path.append(os.path.join(os.getcwd()))
from data_parse.meta import meta, Item
import data_parse.utils as utils
from data_parse.const import FILE_PATH, DST_PATH


def _lines(prefix):
    lines = []
    # init lines as array: [time * 40]
    with open(prefix + 'FN1.DAT', encoding='utf-8') as fp:
        for file_line in fp:
            lines.append(list(filter(lambda str_: len(str_) != 0, [x.strip() for x in file_line.split(',')])))
    # file_num should start from 2
    file_num = 2
    while True:
        filename = prefix + 'FN' + str(file_num) + '.DAT'
        if not os.path.isfile(filename):
            break
        file_num += 1
        with open(filename, encoding='utf-8') as fp:
            for i, file_line in enumerate(fp):
                new_line = list(filter(lambda str_: len(str_) != 0, [x.strip() for x in file_line.split(',')]))
                lines[i].extend(new_line)
    return lines

def _phase_angles(file_result, offset, col_idx, word):
    file_result[Item.phase_angles.name][col_idx - offset]['data'].append(float(word))


def _voltage(file_result, offset, col_idx, word):
    file_result[Item.voltages.name][col_idx - offset]['data'].append(float(word))


def _result(prefix, file_id):
    dstfix = DST_PATH + 'ST_' + file_id + '\\'
    if not os.path.exists(prefix):
        print('Doesn''t exit', prefix)
        return
    if not os.path.exists(dstfix):
        os.mkdir(dstfix)
    # get meta data
    if os.path.exists(dstfix + 'meta.json'):
        f = open(dstfix + 'meta.json', encoding='utf-8')
        file_result = json.load(f)
    else:
        file_result = meta(prefix, dstfix)

    # init offsets lists with meta data
    offsets = [0]
    # voltages power_angles dynamos branch
    offsets.append(offsets[-1] + len(file_result[Item.voltages.name]))
    offsets.append(offsets[-1] + len(file_result[Item.phase_angles.name]))
    for line in _lines(prefix):
        for col_idx, word in enumerate(line):
            offset_idx = next(idx for idx, offset in enumerate(offsets) if offset > col_idx)
            [_voltage, _phase_angles][offset_idx - 1](file_result, offsets[offset_idx - 1], col_idx, word)

    # save it as temporary result
    # install to ../data/st
    print('Writing result.json to: ' + dstfix + ' ...')
    # with open(prefix + 'result.json', 'w') as fp:
    #     json.dump(file_result, fp)
    with open(dstfix + 'phase_angles.json', 'w') as fp:
        json.dump(file_result[Item.phase_angles.name], fp)
    with open(dstfix + 'voltages.json', 'w') as fp:
        json.dump(file_result[Item.voltages.name], fp)


def result():
    """Export this function for install.py"""
    files = utils.get_file_list()
    for i, fileName in enumerate(files):
        if i > 2641:
            _result(FILE_PATH + fileName + '\\', str(i + 1))


if __name__ == '__main__':
    result()
