################################################################################
# Copyright 2018 VAG (Visual Analytics Group), Zhejiang Univ.
################################################################################
import os

# file path
module_dir = os.path.dirname(__file__)
FILE_PATH = 'G:\\beta_eevis_data\\2017_07_01T00_00_00\\'
DST_PATH = module_dir + '\\..\\data\\'
ORIGNIL_SAMPLE_PATH = module_dir + '\\..\\original_sample\\'
# TENSOR_SAMPLE_PATH = module_dir + '\\..\\samples\\'
TENSOR_SAMPLE_PATH = module_dir + '\\..\\samples\\'
TMP_SAMPLE_PATH = module_dir + '\\..\\samples_another_half\\'
# bus info
BUS_NUMBER = 6958

# tensor info
TIMES_STEPS = 2001
FEATRUE_NUMBER = 1902 # 1905 - 3 (3 menas len of unless_bus_id)
# The bus which is filled with zero is unless
UNLESS_BUS_ID = [316, 525, 526]
FAULT_TYPE = 'S'

# sample
ORIGNIL_SAMPLE_NUM = 2663
LABELS_NUM = 2180

# samples that fault center doesn't has value or value are zero
WRONG_SAMPLE_ID = ['13', '75', '343', '579', '581', '687', '787', '789', '791',\
'793', '795', '891', '893', '919', '921', '1031', '1501', '1503', '1547', '1569', \
'1719', '1721', '1723', '1725', '1727', '1729', '1731', '1733', '1735', '1737', \
'1739', '2023', '2111', '2113', '2447', '2541', '2763', '2765', '2767', '2955', \
'2957', '2959', '2961', '2963', '2965', '2967', '2969', '2971', '3019', '3021', \
'4479', '4485', '4487', '4489', '4491', '4493', '4495', '4651', '4887', '4889', \
'4915', '5171', '5173', '5471', '5473', '5475', '5477']
