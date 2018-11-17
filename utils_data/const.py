# const variable for entropy
SPLIT_RANGE = 1000
ENTROPY_RANGE = 20

# const variable for sampling
SAMPLE_THRESHOLD = 0.75
SAMPLE_RATE = 0.25
SAMPLE_FETURE = 475
NO_FILLING = 1    # 1 means no zero filling
                  # 0 means with zeor filling

# for hdf5
BATCH_HDF5 = 534 # 2670 / 5 = 534
# SAX
TIME_STEPS = 2001
PAA_RATE = 11
PAA_W = int(TIME_STEPS / PAA_RATE)
# BREAK_A = 8
# BREAK_POINTS = [-1.15, -0.67, -0.32, 0, 0.32, 0.67, 1.15]
# BREAK_A = 9
# BREAK_POINTS = [-1.22, -0.76, -0.43, -0.14, 0.14, 0.43, 0.76, 1.22]
BREAK_A = 10
#              a      b      c      d      e  f    g      h     i      j  
BREAK_POINTS = [-1.28, -0.84, -0.52, -0.25, 0, 0.25, 0.52, 0.84, 1.28]
tmp_symbol = 'abcdefghijklmnopqrstuvwxyz'
SYMBOLS = [tmp_symbol[i] for i in range(BREAK_A)]
INDEX_S = {}
for i in range(BREAK_A):
    INDEX_S[SYMBOLS[i]] = i
DIST_TABLE = [[0 if abs(r-c) <= 1 else BREAK_POINTS[max(r, c) - 1] - BREAK_POINTS[min(r, c)]\
             for c in range(BREAK_A)]for r in range(BREAK_A)]
# data management files
TENSORE_FILE = 'tensor2D.txt'
TIMES_EXPANSION = 50

# distance compare
## index 0 of element is base element, distance between element[0,1] is low and element[0, 2] is higth
HIGH_VOLTAGE = ['ST_9', 'ST_17', 'ST_866']
LOW_VOLTAGE = ['ST_177', 'ST_1809', 'ST_379']
LOW_HIGH_VOLTAGE = ['ST_200', 'ST_80', 'ST_9']
HIGH_S = ['ST_9', 'ST_11', 'ST_26', 'ST_2640', 'ST_81', 'ST_193']
LOW_S = ['ST_178', 'ST_177', 'ST_200', 'ST_1816', 'ST_597', 'ST_2078']
