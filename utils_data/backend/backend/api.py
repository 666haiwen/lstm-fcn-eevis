import os
import json
import sys
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
    return validate_get_request(request, _get_busData, ['sampleId[]', 'busId'])

def _get_busData(request):
    sampleId = 'ST_' + request.GET.getlist('sampleId[]')[0]
    busId = int(request.GET['busId'])
    x = SAMPLE_DATA[sampleId][:]
    bus_distance = read_json_file(BASE_DIR + '../' + sampleId + '/bus_distance.json')
    i = bus_distance.index(busId)
    return JsonResponse({'data': x[:,i].tolist()})

def get_field(request):
    return validate_get_request(request, _get_field, ['sampleId[]', 'field'])

def _get_field(request):
    sampleId = int(request.GET.getlist('sampleId[]')[0])
    field = int(request.GET['field'])
    fault = FAULTS[sampleId]
    p = [fault['i'], fault['j']]
    visited = [False for i in range(map_size)]
    visited[p[0]] = visited[p[1]] = True
    res = {
        'busId': [],
        'vBase': [],
        'data': [],
        'field': []
    }
    res['field'].append(p.copy())
    bus_distance = read_json_file(BASE_DIR + '../ST_' + str(sampleId) + '/bus_distance.json')
    for i in range(field):
        q = []
        for j in range(map_size):
            if visited[j] or j not in bus_distance:
                continue
            for v in p:
                if v != j and edge_map[v][j] < 1000:
                    q.append(j)
                    break
        for v in p:
            visited[v] = True
        p = q.copy()
        res['field'].append(p.copy())
    # p = []
    # for v in q:
    #     if BUS_INDEX[v] != -1:
    #         p.append(v)
    x = SAMPLE_DATA['ST_' + str(sampleId)][:]
    for p in res['field']:
        for v in p:
            i = bus_distance.index(v)
            res['busId'].append(v)
            res['data'].append(x[:, i].tolist())
            res['vBase'].append(bus_info[v - 1]['vBase'])
    return JsonResponse(res)

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
    return validate_get_request(request, _get_corrcoef, ['sampleId', 'busIds[]'])

def _get_corrcoef(request):
    sampleId = 'ST_' + request.GET['sampleId']
    x = SAMPLE_DATA[sampleId][:]
    bus_distance = read_json_file(BASE_DIR + '../' + sampleId + '/bus_distance.json')
    # # get fixed busIds
    # bus_id = BUS_VBASE.copy()
    # if bus_distance[0] not in bus_id:
    #     bus_id.append(bus_distance[0])
    # if bus_distance[1] not in bus_id:
    #     bus_id.append(bus_distance[1])
    
    # input busIds
    busIds = request.GET.getlist('busIds[]')
    bus_id = [int(v) for v in busIds]
    bus_id = sorted(bus_id)
    vaild_x = np.zeros((x.shape[0], len(bus_id)))
    for i, v in enumerate(bus_id):
        vaild_x[:, i] = x[:, bus_distance.index(v)]
    res = np.corrcoef(vaild_x, rowvar=False)
    max_v = np.max(res)
    min_v = np.min(res)
    return JsonResponse({
        'data': res.tolist(),
        'max': max_v,
        'min': min_v,
        'busDistance': bus_distance,
        'vaild_bus': bus_id
    })

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
