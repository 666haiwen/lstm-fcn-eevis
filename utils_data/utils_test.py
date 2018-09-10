import unittest
import os
import os.path as osp
import sys
sys.path.append(os.getcwd())
sys.path.append(osp.dirname(__file__))
from utils import read_one_case, sampling
import data_parse.const as gl
from const import SAMPLE_RATE, SAMPLE_THRESHOLD, NO_FILLING


class TestClass(unittest.TestCase):
    def test_read_one_case(self):
        path = gl.ORIGNIL_SAMPLE_PATH + 'ST_2/tensor2D.txt'
        read_one_case(path, True)
        wanted_shape = (gl.TIMES_STEPS, gl.FEATRUE_NUMBER)
        self.assertEqual(read_one_case(path).shape, wanted_shape)


    def test_sampling(self):
        path = gl.ORIGNIL_SAMPLE_PATH + 'ST_2/tensor2D.txt'
        tmp_rate = 1
        if NO_FILLING == 1:
            tmp_rate = SAMPLE_RATE
        wanted_shape = (gl.TIMES_STEPS, int(gl.FEATRUE_NUMBER * tmp_rate))
        self.assertEqual(sampling(read_one_case(path)).shape, wanted_shape)


if __name__ == '__main__':
    unittest.main()
    # for i in range(10000):
    #     print(int(380 * (SAMPLE_THRESHOLD - SAMPLE_RATE)))
