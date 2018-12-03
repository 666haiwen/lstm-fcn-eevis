import os
import json
import h5py
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


BUS_DIS = read_json_file(BASE_DIR + 'bus_disinfo.json')
