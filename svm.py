import numpy as np
from sklearn.linear_model import SGDClassifier
import os.path as osp, os
import sys
sys.path.extend([osp.dirname(__file__),
                 osp.join(osp.dirname(__file__), "utils_data")])
from generate_data import DataLoader
from config import cfg


print('Begin load data..\n...\n...\n')
data_loader = DataLoader(seed=cfg.DATA.SPLIT_SEED, weights='default', verbose=True)
X_train, y_train = data_loader.data_read('train', flatten=True)
X_test, y_test = data_loader.data_read('test', flatten=True)

print('Finish load data....\nBegin SGD...\n....\n')
clf = SGDClassifier(alpha=0.001, max_iter=100).fit(X_train, y_train)
pre_res = clf.predict(X_test)
size = len(pre_res)

cnt = 0
for i, label in enumerate(pre_res):
    if label == y_test[i]:
        cnt += 1
print("Result of test:[%d / %d]\nAccuracy:%f %%" % (cnt, size, cnt / size * 100))
