"""
    Copyright 2018-2019 VAG (Visual Analytics Group), Zhejiang Univ.

    Calculate the singel source shorest path for fault center of each sample
"""
import json
import sys
import os
sys.path.append(os.path.join(os.getcwd()))
import data_parse.utils as utils
from data_parse.const import DST_PATH


# create edge map by edge list
def _create_map(edge_list, map_size):
    edge_map = [[sys.float_info.max / 3 for x in range(map_size)] for y in range(map_size)]
    for edge in edge_list:
        # maybe multi lines between i and j ,we accpet min of them
        if edge['dis'] < edge_map[edge['i']][edge['j']]:
            edge_map[edge['i']][edge['j']] = edge_map[edge['j']][edge['i']] = edge['dis']
    for x in range(1, map_size):
        edge_map[x][x] = 0
    return edge_map


# get shortest path from fault center by dijkstra
def _dijkstra(edges_map, map_size, x, y):
    # copy edges_map
    edge_g = [edges[:] for edges in edges_map]
    # one error line = two error buses --> combine to x
    d = [sys.float_info.max / 3 for t in range(map_size)]
    for i in range(1, map_size):
        edge_g[x][i] = edge_g[i][x] = min(edges_map[x][i], edges_map[y][i])
        edge_g[y][i] = edge_g[i][y] = sys.float_info.max / 3
        d[i] = edge_g[x][i]
    d[y] = edge_g[x][y] = edge_g[y][x] = 0
    # begin dijkstra
    used = [False for t in range(map_size)]
    d[x] = 0
    used[x] = True
    for i in range(1, map_size):
        min_v = sys.float_info.max / 3
        t = 0
        for j in range(1, map_size):
            if not used[j] and d[j] < min_v:
                min_v = d[j]
                t = j
        if t == 0:
            break
        used[t] = True
        for k in range(1, map_size):
            if not used[k] and edge_g[t][k] + min_v < d[k]:
                d[k] = edge_g[t][k] + min_v
    return d


def _convert_single_shortest_map(single_dis_map):
    # construct
    points = [{'dist': dist, 'busId': idx} for idx, dist in enumerate(single_dis_map)]
    # filter unreachable points
    points = list(filter(lambda point: point['dist'] != sys.float_info.max, points))
    # sort
    points = sorted(points, key=lambda point: point['dist'])
    # append
    return list(map(lambda point: point['busId'], points))


def _create_shortest_path(prefix):
    # get vertex and edge
    buses = utils.get_json_file(prefix, 'bus_info.json')
    edges = utils.get_json_file(prefix, 'edge_info.json')
    faults = utils.get_json_file(prefix, 'fault.json')
    # create map and index from 1 not 0 --> size = len + 1
    map_size = len(buses) + 1
    edge_map = _create_map(edges, map_size)
    # construct shortest path between map by different fault center
    for i, fault in enumerate(faults):
        if i < 2828:
            continue
        # get fault center
        x = fault['i']
        y = fault['j']
        dijkstra = _dijkstra(edge_map, map_size, x, y)
        sorted_id_list = _convert_single_shortest_map(dijkstra)
        # install to ../data/ST_id/
        result = {
            'x': x,
            'y': y,
            'busIds': sorted_id_list
        }
        dstfix = DST_PATH + 'ST_' + fault['st'] + '\\'
        print('Writing shortest_path.json to:' + dstfix + ' ...')
        # write file to that directory
        with open(dstfix + 'shortest_path.json', 'w') as fp:
            json.dump(result, fp)


def floyd():
    """Export this function for install.py"""
    _create_shortest_path(DST_PATH + 'data\\')


if __name__ == '__main__':
    floyd()
