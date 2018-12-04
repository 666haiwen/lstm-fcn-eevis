import os
import json
from django.http import *
import numpy as np
from .utils import *


def get_tsne(request):
    return validate_get_request(request, _get_tsne)


def _get_tsne(request):
    pos = read_json_file(BASE_DIR + 'tsne-euclidean.json')
    res = {
        'pos': pos['pos'],
        'fault': FAULTS,
        # 'bus_dis': BUS_DIS,
    }
    return JsonResponse(res)

def get_birch(request):
    return validate_get_request(request, _get_birch, ['name'])

def _get_birch(request):
    name = request.GET['name']
    return JsonResponse(read_json_file(BASE_DIR + 'birch/' + name))

def get_busData(request):
    return validate_get_request(request, _get_busData, ['sampleId', 'busId'])

def _get_busData(request):
    sampleId = 'ST_' + request.GET['sampleId']
    busId = int(request.GET['busId'])
    x = SAMPLE_DATA[sampleId][:]
    bus_distance = read_json_file(BASE_DIR + '../' + sampleId + '/bus_distance.json')
    i = bus_distance.index(busId)
    return JsonResponse({'data': x[:,i].tolist()})

def get_sampleDis(request):
    return validate_get_request(request, _get_sampleDis, ['sampleId[]'])

def _get_sampleDis(request):
    sampleId = request.GET.getlist('sampleId[]')
    dis = []
    for i in sampleId:
        tmp_dis = []
        for j in sampleId:
            tmp_dis.append(get_MinDis(FAULTS[int(i)], FAULTS[int(j)]))
        dis.append(tmp_dis)
    return JsonResponse({'dis': dis})

def get_busDistance(request):
    return validate_get_request(request, _get_busDistance, ['idx', 'idy'])

def _get_busDistance(request):
    idx = request.GET['idx']
    idy = request.GET['idy']
    bus_a = read_json_file(BASE_DIR + '../ST_' + idx + '/bus_distance.json')
    bus_b = read_json_file(BASE_DIR + '../ST_' + idy + '/bus_distance.json')
    res = [bus_b.index(bus_a[0]), bus_b.index(bus_a[1]),\
           bus_a.index(bus_b[0]), bus_a.index(bus_b[1])]
    return JsonResponse({'data': res})

def get_corrcoef(request):
    return validate_get_request(request, _get_corrcoef, ['sampleId'])

def _get_corrcoef(request):
    sampleId = 'ST_' + request.GET['sampleId']
    x = SAMPLE_DATA[sampleId][:]
    res = np.corrcoef(x, rowvar=False)
    max_v = np.max(res)
    min_v = np.min(res)
    bus_distance = read_json_file(BASE_DIR + '../' + sampleId + '/bus_distance.json')
    return JsonResponse({'data': res.tolist(), 'max': max_v, 'min': min_v, 'busDistance': bus_distance})

def get_forceInfo(request):
    return validate_get_request(request, _get_forceInfo)

def _get_forceInfo(request):
    # disInfo = read_json_file(BASE_DIR + 'dis_info.json')
    busInfo = read_json_file(BASE_DIR + 'bus_info.json')
    edgeInfo = read_json_file(BASE_DIR + 'edge_info.json')
    bus_valid = read_json_file(BASE_DIR + 'bus_valid.json')
    bus_index = read_json_file(BASE_DIR + 'bus_index.json')
    res = {
        # 'disInfo': disInfo['dis'],
        'busInfo': [],
        'edgeInfo': [],
        'bus_vaild': bus_valid
    }
    for bus in bus_valid:
        res['busInfo'].append({
            'id': busInfo[bus - 1]['busId'],
            'vBase': busInfo[bus - 1]['vBase']
        })
    for edge in edgeInfo:
        if bus_index[edge['i']] != -1 and bus_index[edge['j']] != -1:
            res['edgeInfo'].append({
                'source': edge['i'],
                'target': edge['j'],
                'value':edge['dis']
            })
    return JsonResponse(res)
