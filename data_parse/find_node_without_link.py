"""
    Copyright 2018-2019 VAG (Visual Analytics Group), Zhejiang Univ.

    Just to get the node which are no linked
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd()))
import data_parse.const as gl
import data_parse.utils as utils


def find_node_without_link():
    edges = utils.get_json_file(gl.DST_PATH + 'data\\', 'edge_info.json')
    flag = [False for i in range(gl.BUS_NUMBER + 1)]
    for edge in edges:
        flag[edge['i']] = True
        flag[edge['j']] = True
    node_res = []
    for i in range(gl.BUS_NUMBER + 1):
        if not flag[i]:
            node_res.append(i)
    print('len of node_res : ' + str(len(node_res)))
    print(node_res)


if __name__ == '__main__':
    find_node_without_link()
