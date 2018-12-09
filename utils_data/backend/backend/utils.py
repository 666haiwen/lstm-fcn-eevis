import os
import json
import h5py
import sys
import numpy as np
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest


BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '../../',
    'original_sample', 'data/'
)

SAMPLE_DATA = h5py.File(BASE_DIR + 'orignal_sample.hdf5', 'r')

def calc_prefix(request):
    type_id, sample_id = request.GET['type'], request.GET['sample']
    return os.path.join(BASE_DIR, type_id, 'ST_' + sample_id)


def validate_get_request(request, func, accept_params=None, args=None):
    """Check if method of request is GET and request params is legal

    Args:
         request: request data given by django
         func: function type, get request and return HTTP response
         accept_params: list type, acceptable parameter list

    Returns:
         HTTP response
    """
    if accept_params is None:
        accept_params = []
    if args is None:
        args = []
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    elif set(accept_params).issubset(set(request.GET)):
        return func(request, *args)
    else:
        return HttpResponseBadRequest('parameter lost!')


def read_txt_file(filepath):
    try:
        tensor = np.loadtxt(filepath)
        return { 'data': tensor.tolist() }
    except EnvironmentError:
        return { 'error': 'File not found!' }


def read_json_file(filepath):
    try:
        with open(filepath, encoding='utf-8') as fp:
            return json.load(fp)
    except EnvironmentError:
        return { 'error' : 'File not found!' }


def get_MinDis(a, b):
    bus_a = [BUS_INDEX[a['i']], BUS_INDEX[a['j']]]
    bus_b = [BUS_INDEX[b['i']], BUS_INDEX[b['j']]]
    # print(len(BUS_DIS))
    # print(bus_a[0], bus_b[1])
    # print(BUS_DIS[bus_a[0]][bus_b[1]])
    # print(BUS_DIS[bus_a[1]][bus_b[0]], BUS_DIS[bus_a[1]][bus_b[1]])
    return min(BUS_DIS[bus_a[0]][bus_b[0]], BUS_DIS[bus_a[0]][bus_b[1]], \
        BUS_DIS[bus_a[1]][bus_b[0]], BUS_DIS[bus_a[1]][bus_b[1]])

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


BUS_DIS = read_json_file(BASE_DIR + 'bus_disinfo.json')['dis']
BUS_INDEX = read_json_file(BASE_DIR + 'bus_index.json')
FAULTS = []
faultList = read_json_file(BASE_DIR + 'fault_list.json')['fault_list']
faultMark = read_json_file(BASE_DIR + 'fault_mark.json')
for f in faultMark:
    FAULTS.append(faultList[f['mark']])
BUS_VBASE = [24, 38, 51, 71, 79, 113, 114, 115, 116, 117, 156, 161, 180, 213, 220, 227, 243, 262, 273, 315, 333, 354, 364, 383, 427, 441, 460, 465, 481, 487, 498, 518, 524, 547, 560, 575, 601, 608, 629, 646, 653, 675, 692, 696, 702, 719, 731, 742, 749, 759, 858, 859, 871, 878, 886, 912, 917, 928, 929, 936, 944, 965, 978, 1199, 1221, 1237, 1241, 1246, 1264, 1279, 1283, 1288, 1354, 1358, 1363, 1367, 1946, 1987, 1999, 2044, 2389, 2424, 5012, 5047, 5061, 5122, 5123, 5126, 5159, 5227, 5228, 5229, 5230, 5275, 5278, 5337, 5338]
edges = read_json_file(BASE_DIR + 'edge_info.json')
bus_info = read_json_file(BASE_DIR + 'bus_info.json')
map_size = 6958 + 1
edge_map = _create_map(edges, map_size)
