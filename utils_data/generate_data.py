from __future__ import absolute_import, division, print_function

import os.path as osp
import re
import sys
import threading
sys.path.append(osp.join(osp.dirname(__file__), ".."))
from collections import Iterable
from glob import glob
from hashlib import md5

import numpy as np
from sklearn.model_selection import train_test_split

from utils import read_a_set_labels, read_one_case
from config import cfg


class ThreadSafeIter(object):
    """Takes an iterator/generator and makes it thread-safe by
    serializing call to the `next` method of given iterator/generator.
    """
    def __init__(self, it):
        self.it = it
        self.lock = threading.Lock()
        
    def __iter__(self):
        return self
    
    def __next__(self):
        with self.lock:
            return next(self.it)

def threadSafeGenerator(f):
    """ A decorator that takes a generator function and makes it thread-safe. """
    def g(*a, **kw):
        return ThreadSafeIter(f(*a, **kw))
    return g


class DataSet(object):
    def __init__(self, tag=None):
        self._paths = []
        self._labels = []
        self._num_of_paths = 0
        self._num_of_labels = 0
        if tag is not None:
            self.tag = tag

    def __repr__(self):
        m = md5()
        m.update(''.join(self._paths).encode('utf-8'))
        digest = m.hexdigest()
        return "DataSet({} data: {}  labels: {}), Finger({})".format(self.tag, len(self.paths), len(self.labels), digest)

    @property
    def paths(self):
        return self._paths

    @paths.setter
    def paths(self, new_paths):
        self._paths = new_paths
        self._num_of_paths = len(new_paths)

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, new_labels):
        self._labels = new_labels
        self._num_of_labels = len(new_labels)

    @property
    def num_of_paths(self):
        return self._num_of_paths
    
    @property
    def num_of_labels(self):
        return self._num_of_labels


class DataLoader(object):
    def __init__(self, seed=None, weights=None, verbose=False):
        self.all_txt_paths = []
        self.all_labels = []
        self.all_classes = None
        self.num_of_examples = self._get_paths_and_labels(verbose=verbose)
        self.num_of_classes = self._get_classes(verbose=verbose)
        
        self.train = DataSet("train")
        self.val = DataSet("validation")
        self.test = DataSet("test")
        self._split_dataset(seed=seed, verbose=verbose)
        self.dataset = {"train": self.train, "validation": self.val, "test": self.test}

        if weights is None:
            self.class_weights = None
        elif weights == 'default':
            self.class_weights = self._get_default_weights()
        elif isinstance(weights, Iterable) and len(weights) == self.num_of_classes:
            self.class_weights = np.array(weights)
        else:
            raise ValueError("Wrong parameter: `weights`")



    def _get_paths_and_labels(self, verbose=False):
        """ Load data paths and labels, and save them as two lists.

        Paramas
        -------
        `verbose`: display data info or not
        """
        # grids_list = glob(osp.join(cfg.DATA.ROOT_DIR, "*"))
        # for grid in grids_list:
            # real data
        ST_list = glob(osp.join(cfg.DATA.ROOT_DIR, "ST_*"))
        labels = read_a_set_labels(osp.join(cfg.DATA.ROOT_DIR, cfg.DATA.LAB_FILE))
        remove_list = []
        for i, ST in enumerate(ST_list):
            basename = osp.basename(ST)
            if not basename in labels.keys():
                remove_list.append(ST)
            else:
                self.all_labels.append(labels[basename])
                ST_list[i] = osp.join(ST_list[i], cfg.DATA.OBJ_FILE)
        for ST in remove_list:
            ST_list.remove(ST)
        self.all_txt_paths.extend(ST_list)

        # fake data
        # FAKE_list = glob(osp.join(grid, cfg.DATA.FAKE_FILE))
        # self.all_txt_paths.extend(FAKE_list)
        # self.all_labels.extend([cfg.DATA.FAKE_CLASS] * len(FAKE_list))    # NEW labels normal(fake) data

        assert len(self.all_labels) == len(self.all_txt_paths)

        num_of_labels = len(self.all_labels)
        num_of_examples = len(self.all_txt_paths)
        if verbose:
            print("Number of labels:", num_of_labels)
            print("Number of examples:", num_of_examples)

        assert num_of_labels == num_of_examples, \
            "Number of labels({}) doesn't equal to number of examples({})!".format(num_of_labels, num_of_examples)

        return num_of_examples

    def _get_classes(self, verbose=False):
        self.all_classes = np.lib.arraysetops.unique(self.all_labels)
        num_of_classes = len(self.all_classes)
        if verbose:
            print("Number of classes:", num_of_classes)

        assert num_of_classes == cfg.DATA.NUM_CLASSES
        return num_of_classes

    def check_data_label_pair(self, num=20, seed=None):
        np.random.seed(seed)
        indexes = np.random.choice(range(self.num_of_examples), num, replace=False)
        all_cases = list(zip(self.all_txt_paths, self.all_labels))
        for idx in indexes:
            one_case = all_cases[idx]
            paths = re.split('\\\\|/', one_case[0])
            if "normal" in paths[-1]:
                assert one_case[1] == 4, \
                    "Data({}) and label({}) mismatch!".format(*one_case)
            else:
                labels_path = osp.join(cfg.DATA.ROOT_DIR, paths[-3], cfg.DATA.LAB_FILE)
                labels = read_a_set_labels(labels_path)
                assert labels[paths[-2]] == one_case[1], \
                    "Data({}) and label({}) mismatch!".format(*one_case)
        print("Matching check finished!")

    def _split_dataset(self, seed=None, verbose=False):
        
        # check ratio
        assert cfg.DATA.TRAIN_RATIO + cfg.DATA.VAL_RATIO + cfg.DATA.TEST_RATIO == 1

        # split dataset into train/validation/test three parts
        self.train.paths, X, self.train.labels, y = train_test_split(self.all_txt_paths, self.all_labels, 
                                                                     train_size=cfg.DATA.TRAIN_RATIO,
                                                                     random_state=seed)
        val_over_val_plus_test = cfg.DATA.VAL_RATIO / (cfg.DATA.VAL_RATIO + cfg.DATA.TEST_RATIO)
        self.val.paths, self.test.paths, self.val.labels, self.test.labels = train_test_split(X, y,
                                                                     train_size=val_over_val_plus_test,
                                                                     random_state=seed)
        if verbose:
            print(self.train)
            print(self.val)
            print(self.test)

    def _get_default_weights(self):
        num_per_class = np.bincount(self.all_labels).astype(np.float)
        return self.num_of_examples / (self.num_of_classes * num_per_class)

    def _one_hot(self, target, output):
        target.flatten()
        num_samples = target.shape[0]
        output[...] = 0
        output[np.arange(num_samples), target] = 1


    @threadSafeGenerator
    def generator(self, tag, batch_size, use_weights=False, seed=None):
        if not tag in ['train', 'validation', 'test']:
            raise ValueError("Parameter `tag` mush belong to ['train', 'validation', 'test']!")

        np.random.seed(seed)
        all_cases = list(zip(self.dataset[tag].paths, self.dataset[tag].labels))

        # placeholder for data and labels
        data = np.empty(shape=(batch_size, cfg.TIME_STEPS, cfg.FEATURES))
        targets = np.zeros(shape=(batch_size, self.num_of_classes))

        while True:
            np.random.shuffle(all_cases)
            temp = list(zip(*all_cases))
            data_paths = temp[0]
            labels = np.array(temp[1])
            iter = 0
            while iter + batch_size < self.dataset[tag].num_of_paths:
                for i in range(batch_size):
                    data[i] = read_one_case(data_paths[iter + i])
                self._one_hot(labels[iter:iter + batch_size], targets)

                if not use_weights or self.class_weights is None:
                    yield data, targets
                else:
                    weights = self.class_weights[targets]
                    yield data, targets, weights
                iter += batch_size


    def data_read(self, tag, seed=None, flatten=False):
        """
            Read sample data into memory
        """
        if not tag in ['train', 'validation', 'test']:
            raise ValueError("Parameter `tag` mush belong to ['train', 'validation', 'test']!")

        np.random.seed(seed)
        # all_cases = list(zip(self.dataset[tag].paths, self.dataset[tag].labels))
        labels = np.array(self.dataset[tag].labels)
        size = len(self.dataset[tag].labels)
        if flatten:
            data = np.empty(shape=(size, cfg.TIME_STEPS * cfg.FEATURES))
        else:            
            data = np.empty(shape=(size, cfg.TIME_STEPS, cfg.FEATURES))
            targets = np.zeros(shape=(size, self.num_of_classes))
        for i, path in enumerate(self.dataset[tag].paths):
            if i%1000 == 0:
                print('Load {} samples!'.format(i))
            data[i] = read_one_case(path, flatten=flatten)
        print('Finish Read Data into Memory!')
        if flatten:
            return data, labels
        self._one_hot(labels, targets)
        return data, targets


if __name__ == '__main__':
    if True:
        loader = DataLoader(seed=1236, verbose=True, weights='default')
        x, y, weights = loader.data_read('test', 1234)
        print()
        # loader.check_data_label_pair(seed=1234)
        # i = 0
        # for data, targets in loader.generator("train", 10, seed=1234):
        #     if i > 6:
        #         break
        #     print(targets)
        #     print('sizeof', sys.getsizeof(data))
        #     i += 1
