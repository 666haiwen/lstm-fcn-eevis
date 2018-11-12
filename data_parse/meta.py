"""
    Copyright 2018-2019 VAG (Visual Analytics Group), Zhejiang Univ.

    Preparing for meta json and run for result.py
"""
import json
from enum import Enum

# 2 12
class Item(Enum):
    voltages = 2
    phase_angles = 12


def meta(prefix, dstfix):
    meta_result = {
        Item.voltages.name:[],
        Item.phase_angles.name:[]
    }
    with open(prefix + 'STOUT.INF', 'r') as fp:
        prev_item = -1
        for i, fp_line in enumerate(fp):
            line = list(filter(lambda str : len(str) != 0,
                [x.strip() for x in fp_line.split(',')]))
            item = int(line[1])
            if item != 99:
                _switch(item, meta_result, line[2: len(line)])
                prev_item = item
            else:
                _switch(prev_item, meta_result, line[2: len(line)])
    # with open(dstfix + 'meta.json', 'w') as fp:
    #     json.dump(meta_result, fp, indent = 2, ensure_ascii=False)
    return meta_result


def _switch(item, meta_result, line):
    if item == Item.voltages.value:
        _voltages(meta_result, line)
    elif item == Item.phase_angles.value:
        _phase_angles(meta_result, line)


def _voltages(meta_result, bus_ids):
    for bus_id in bus_ids:
        if bus_id == '0':
            break
        meta_result[Item.voltages.name].append({
            'busId' : int(bus_id),
            'data' : []
        })

# bus_ids : str
def _phase_angles(meta_result, bus_ids):
    for i in range(0, len(bus_ids), 2):
        bus_id = bus_ids[i]
        if bus_id == '0':
            break
        meta_result[Item.phase_angles.name].append({
            'busId' : int(bus_id),
            'data' : []
        })
