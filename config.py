import os.path as osp

from easydict import EasyDict as edict


Windows = True

_C = edict()
cfg = _C

_C.PROJECT_DIR = osp.dirname(__file__)

_C.TIME_STEPS = 2001 #501

_C.FEATURES = 475 #1902 * 0.25 #380*0.25  # 540

""" #################################################################
    Data parameters
"""
_C.DATA = edict()

# Data in this directory is belong to 20 grids
if Windows:
    _C.DATA.ROOT_DIR = "G:/LSTM-EEVIS/samples"
else:
    _C.DATA.ROOT_DIR = "/data"

_C.DATA.OBJ_FILE = "tensor2D.txt"

_C.DATA.LAB_FILE = "data/_fault_mark.json"

_C.DATA.FAKE_FILE = "data/tensor2D_normal_*.txt"

_C.DATA.NUM_CLASSES = 2180

_C.DATA.FAKE_CLASS = 2181

_C.DATA.PREFIX = "grid"

_C.DATA.TRAIN_RATIO = 0.6

_C.DATA.VAL_RATIO = 0.2

_C.DATA.TEST_RATIO = 0.2

_C.DATA.SPLIT_SEED = 1234


""" #################################################################
    Training parameters
"""
_C.TRAIN = edict()

_C.TRAIN.EPOCHS = 250

_C.TRAIN.BATCH_SIZE =  128 #128

_C.TRAIN.LR = 1e-4  # 1e-3 before

_C.TRAIN.MIN_LR = 1e-7 # 1e-4 before

_C.TRAIN.WORKERS = 4

_C.TRAIN.MAX_QUEUE_SIZE = 20

""" #################################################################
    Evaluate parameters
"""
_C.TEST = edict()

_C.TEST.BATCH_SIZE = 128 #64

_C.TEST.MAX_QUEUE_SIZE = 20

_C.TEST.WORKERS = 4


""" #################################################################
    Model parameters
"""
_C.MODEL = edict()

# squeeze and excitation block ratio
_C.MODEL.SE_RATIO = 16

_C.MODEL.SAVE_PATH = osp.join(osp.dirname(__file__), "save")

_C.MODEL.LOG_PATH = osp.join(osp.dirname(__file__), "logs")
