import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.getcwd())
import utils_data.cluster.distance as dt
import utils_data.const as st
import data_parse.const as gl
from data_parse.utils import get_json_file


def distance_test(a, b, name):
    """ calculate diffierent distance between sample a and sample b

    a,b : string sample id in samples, named in 'ST_***', *** is a number
    """
    path = gl.ORIGNIL_SAMPLE_PATH
    x = np.loadtxt(path + a + '/tensor2D.txt')
    y = np.loadtxt(path + b + '/tensor2D.txt')
    a_bus = get_json_file(path + a, '/bus_distance.json')
    b_bus = get_json_file(path + b, '/bus_distance.json')
    length = len(a_bus)
    for i in range(length):
        a_bus[i] = {'index': i, 'value': a_bus[i]}
        b_bus[i] = {'index': i, 'value': b_bus[i]}
    a_bus.sort(key=lambda v: v['value'])
    b_bus.sort(key=lambda v: v['value'])
    shape = x.shape
    _x = np.zeros(shape)
    _y = np.zeros(shape)
    for col in range(shape[1]):
        _x[:, col] = x[:, a_bus[col]['index']]
        _y[:, col] = y[:, b_bus[col]['index']]
    
    busid_sort = []
    for v in a_bus:
        busid_sort.append(v['value'])
    if not os.path.exists(path + 'busid_sort.json'):
        with open(path + 'busid_sort.json', 'w', encoding='utf-8') as fp:
            json.dump(busid_sort, fp)

    file_name = path + a + '-' + b + '-' + name + '.txt'
    if os.path.exists(file_name):
        _dis = np.loadtxt(file_name)
        shape = _dis.shape
        dis = np.zeros((10, shape[1]))
        dis[:shape[0], :] = _dis
        # dis[0] = dt.euclidean(_x, _y, 2)
        # dis[1] = dt.related(_x, _y, 2)
        # dis[3] = dt.euclidean(_x, _y, 1)
        dis[5] = dt.kullback_Liebler(_x, _y, 20)
        # dis[6] = dt.j_divergence(_x, _y)
        # dis[7] = dt.base_LPC(_x, _y)
        # dis[8] = dt.pca_based(_x, _y)
    else:
        dis = np.zeros((10, shape[1]))
        dis[0] = dt.euclidean(_x, _y, 2)
        dis[1] = dt.related(_x, _y, 2)
        dis[2] = dt.sts(_x, _y)
        # dis[3] = dt.dtw(_x, _y)
        # dis[4] = dt.probability_based(_x, _y)
        dis[5] = dt.kullback_Liebler(_x, _y, 20)
        # dis[6] = dt.j_divergence(_x, _y)
        dis[7] = dt.base_LPC(_x, _y)
        # dis[8] = dt.pca_based(_x, _y)
    print('distance between {} and {}, saving to {}'.format(a, b, path))
    np.savetxt(path + a + '-' + b + '-' + name + '.txt', dis, fmt='%.8e')


def distance_plot(a, b, name):
    path = gl.ORIGNIL_SAMPLE_PATH
    file_name = gl.ORIGNIL_SAMPLE_PATH + a + '-' + b + '-' + name + '.txt'
    y = np.loadtxt(file_name)
    y = np.nan_to_num(y)
    x = [i for i in range(gl.FEATRUE_NUMBER)]
    shape = y.shape
    for row in range(shape[0]):
        tmp = np.mean(y[row])
        y[row] = y[row] + tmp - y[row]
    a_bus = get_json_file(path + a, '/bus_distance.json')
    b_bus = get_json_file(path + b, '/bus_distance.json')
    bus_sort = get_json_file(path, 'busid_sort.json')
    plt.scatter(bus_sort.index(a_bus[0]), -1, marker='x', color='b')
    plt.scatter(bus_sort.index(a_bus[1]), -1, marker='x', color='b')
    plt.scatter(bus_sort.index(b_bus[0]), -1, marker='o', color='r')
    plt.scatter(bus_sort.index(b_bus[1]), -1, marker='o', color='r')

    plt.plot(x, y[0], color='#ec7014', label='Euclidean')
    plt.plot(x, y[1], color='#ccebc5', label='Related')
    plt.plot(x, y[2], color='#a8ddb5', label='STS')
    plt.plot(x, y[3], color='#fc4e2a', label='DTW')
    # plt.plot(x, y[4], color='#4eb3d3', label='Chi2')
    plt.plot(x, y[5], color='#2b8cbe', label='Markov')
    plt.plot(x, y[7], color='#4a1486', label='LPC')
    plt.plot(x, y[8], color='#636363', label='PCA')
    plt.title(name)
    plt.xlabel('bus')
    plt.ylabel('distance')
    plt.legend()
    plt.show()


def find_compared_sample():
    """ find compared sample that
        close/far between (high-v, hight-v), (low-v, low-v), (low-v, high-v)

        Returns:
        hight, low, high-low: list, len = 3
    """
    path = gl.ORIGNIL_SAMPLE_PATH
    fault_list = get_json_file(path + 'data\\', 'fault_list.json')['fault_list']
    fault_mark = get_json_file(path + 'data\\', 'fault_mark.json')
    bus_info = get_json_file(gl.DST_PATH + 'data\\', 'bus_info.json')
    high_v_index = []
    low_v_index = []
    for i, fault_m in enumerate(fault_mark):
        fault_c = fault_list[fault_m['mark']]
        # pass normal sample
        if i == 0:
            continue
        v_base_i = bus_info[fault_c['i'] - 1]['vBase']
        v_base_j = bus_info[fault_c['j'] - 1]['vBase']
        if v_base_i < 200 and v_base_j < 200:
            low_v_index.append({'st': i, 'fault_center': fault_c})
        if v_base_i > 500 and v_base_j > 500:
            high_v_index.append({'st': i, 'fault_center': fault_c})

    # find sample based on distance
    def find_distance_sample(v_list, cmp_base):
        """ find sample which is close/far from cmp_base in v_list
        """
        st_file = 'ST_' + str(cmp_base['st']) + '/'
        bus_distance = get_json_file(path + st_file, 'bus_distance.json')
        close_list = []
        far_list = []
        one_same_list = []
        for v_st in v_list:
            if v_st['fault_center']['i'] == cmp_base['fault_center']['i']:
                if v_st['fault_center']['j'] == cmp_base['fault_center']['j']:
                    continue
                else:
                    one_same_list.append(v_st['st'])
            if v_st['fault_center']['i'] == cmp_base['fault_center']['j']:
                if v_st['fault_center']['j'] == cmp_base['fault_center']['i']:
                    continue
                else:
                    one_same_list.append(v_st['st'])
            if bus_distance.index(v_st['fault_center']['i']) < 20:
                close_list.append(v_st['st'])
            if bus_distance.index(v_st['fault_center']['i']) > 500:
                far_list.append(v_st['st'])
        return (close_list, far_list, one_same_list)

    res = {
        'high-high':[],
        'low-low':[],
        'low-high':[]
    }
    for x in high_v_index:
        list_r = find_distance_sample(high_v_index, x)
        if len(list_r[0]) != 0 and len(list_r[1]) != 0:
            res['high-high'].append({
                'b': x,
                'c': list_r[0],
                'f': list_r[1],
                'o': list_r[2]
            })
    for x in low_v_index:
        list_r = find_distance_sample(low_v_index, x)
        if len(list_r[0]) != 0 and len(list_r[1]) != 0:
            res['low-low'].append({
                'b': x,
                'c': list_r[0],
                'f': list_r[1],
                'o': list_r[2]
            })
    for x in low_v_index:
        list_r = find_distance_sample(high_v_index, x)
        if len(list_r[0]) != 0 and len(list_r[1]) != 0:
            res['low-high'].append({
                'b': x,
                'c': list_r[0],
                'f': list_r[1],
                'o': list_r[2]
            })
    print('Writing compared_samples.json to ' + path)
    with open(path + 'compared_samples.json', 'w', encoding='utf-8') as fp:
        json.dump(res, fp)


def pca_test():
    path = gl.ORIGNIL_SAMPLE_PATH
    samples = get_json_file(path, 'compared_samples.json')
    def get_pca_res(st_a, st_b):
        x = np.loadtxt(path + 'ST_{}'.format(st_a) + '/tensor2D.txt')
        y = np.loadtxt(path + 'ST_{}'.format(st_b) + '/tensor2D.txt')
        a_bus = get_json_file(path + 'ST_{}'.format(st_a), '/bus_distance.json')
        b_bus = get_json_file(path + 'ST_{}'.format(st_b), '/bus_distance.json')
        length = len(a_bus)
        for i in range(length):
            a_bus[i] = {'index': i, 'value': a_bus[i]}
            b_bus[i] = {'index': i, 'value': b_bus[i]}
        a_bus.sort(key=lambda v: v['value'])
        b_bus.sort(key=lambda v: v['value'])
        shape = x.shape
        _x = np.zeros(shape)
        _y = np.zeros(shape)
        for col in range(shape[1]):
            _x[:, col] = x[:, a_bus[col]['index']]
            _y[:, col] = y[:, b_bus[col]['index']]
        return dt.pca_based(_x, _y)
    
    PCA_TEST_NUM = 10
    res = {'hch':[], 'hfh':[], 'lcl':[], 'lfl':[], 'lch':[], 'lfh':[]}
    def get_res(i_type, o_c, o_f):
        c_num = f_num = 0
        for sample in samples[i_type]:
            b = sample['b']['st']
            for c in sample['c']:
                if c_num < PCA_TEST_NUM:
                    res[o_c].append({'a_st': b, 'b_st': c, 'dis': get_pca_res(b, c)})
                    c_num += 1
            for f in sample['f']:
                if f_num < PCA_TEST_NUM:
                    res[o_f].append({'a_st': b, 'b_st': f, 'dis': get_pca_res(b, f)})
                    f_num += 1
    
    get_res('high-high', 'hch', 'hfh')
    get_res('low-low', 'lcl', 'lfl')
    get_res('low-high', 'lch', 'lfh')
    with open(path + 'pca_dis_res.json', 'w', encoding='utf-8') as fp:
        print('Writing pca_dis_res.json to ' + path)
        json.dump(res, fp)


def plot_pca():
    path = gl.ORIGNIL_SAMPLE_PATH
    dis = get_json_file(path, 'pca_dis_res.json')
    x = [i for i in range(10)]
    def plot_one_line(y, color, label):
        y = [v['dis'] for v in y]
        plt.plot(x, y, color=color, label=label)
    
    plot_one_line(dis['hch'], '#ccebc5', 'hch')
    plot_one_line(dis['hfh'], '#a8ddb5', 'hfh')
    plot_one_line(dis['lcl'], '#fc4e2a', 'lcl')
    plot_one_line(dis['lfl'], '#2b8cbe', 'lfl')
    plot_one_line(dis['lch'], '#4a1486', 'lch')
    plot_one_line(dis['lfh'], '#636363', 'lfh')
    plt.title('PCA RES')
    plt.xlabel('samples')
    plt.ylabel('distance')
    plt.legend()
    plt.show()

# calculate distance
# distance_test(st.HIGH_VOLTAGE[0], st.HIGH_VOLTAGE[1], 'high-close-high')
# distance_test(st.HIGH_VOLTAGE[0], st.HIGH_VOLTAGE[2], 'high-far-high')
# distance_test(st.LOW_VOLTAGE[0], st.LOW_VOLTAGE[1], 'low-close-low')
# distance_test(st.LOW_VOLTAGE[0], st.LOW_VOLTAGE[2], 'low-far-low')
# distance_test(st.LOW_HIGH_VOLTAGE[0], st.LOW_HIGH_VOLTAGE[1], 'low-close-high')
# distance_test(st.LOW_HIGH_VOLTAGE[0], st.LOW_HIGH_VOLTAGE[2], 'low-far-high')
# distance_test(st.HIGH_S[0], st.HIGH_S[1], 'HIGH-S-0')
# distance_test(st.HIGH_S[2], st.HIGH_S[3], 'HIGH-S-1')
# distance_test(st.HIGH_S[4], st.HIGH_S[5], 'HIGH-S-2')
# distance_test(st.LOW_S[0], st.LOW_S[1], 'LOW-S-0')
# distance_test(st.LOW_S[2], st.LOW_S[3], 'LOW-S-1')
# distance_test(st.LOW_S[4], st.LOW_S[5], 'LOW-S-2')

# plot distance
distance_plot(st.HIGH_VOLTAGE[0], st.HIGH_VOLTAGE[1], 'high-close-high')
distance_plot(st.HIGH_VOLTAGE[0], st.HIGH_VOLTAGE[2], 'high-far-high')
distance_plot(st.LOW_VOLTAGE[0], st.LOW_VOLTAGE[1], 'low-close-low')
distance_plot(st.LOW_VOLTAGE[0], st.LOW_VOLTAGE[2], 'low-far-low')
distance_plot(st.LOW_HIGH_VOLTAGE[0], st.LOW_HIGH_VOLTAGE[1], 'low-close-high')
distance_plot(st.LOW_HIGH_VOLTAGE[0], st.LOW_HIGH_VOLTAGE[2], 'low-far-high')
distance_plot(st.HIGH_S[0], st.HIGH_S[1], 'HIGH-S-0')
distance_plot(st.HIGH_S[2], st.HIGH_S[3], 'HIGH-S-1')
distance_plot(st.HIGH_S[4], st.HIGH_S[5], 'HIGH-S-2')
distance_plot(st.LOW_S[0], st.LOW_S[1], 'LOW-S-0')
distance_plot(st.LOW_S[2], st.LOW_S[3], 'LOW-S-1')
distance_plot(st.LOW_S[4], st.LOW_S[5], 'LOW-S-2')

# find sample to compare
# find_compared_sample()

# pca test
# pca_test()
# plot_pca()
