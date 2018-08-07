import unittest

import os.path as osp
import sys
sys.path.append(osp.dirname(__file__))
from utils import read_one_case, sampling
import const as gl

class TestClass(unittest.TestCase):

    def test_read_one_case(self):
        path = r"F:/Workspace/LSTM/MLSTM-src/data/1/ST_2/tensor2D.txt"
        wanted_shape = (501, 540)
        self.assertEqual(read_one_case(path).shape, wanted_shape)

    def test_sampling(self):
        path = r"F:/Workspace/LSTM/MLSTM-src/sampleData/1/51/tensor2D.txt"
        wanted_shape = (501, 380)
        self.assertEqual(sampling(read_one_case(path)).shape, wanted_shape)

if __name__ == '__main__':
    # unittest.main()
    for i in range(10000):
        print(int(380 * (gl.SAMPLE_THRESHOLD - gl.SAMPLE_RATE)))
