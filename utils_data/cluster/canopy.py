# Authors: Chen zexian(zjuczx@zju.edu.cn)
import os
import sys
import numpy as np
from utils_data.cluster.dataset import get_dis_matrix


def name2id(name):
    return int(name[3:])


class Canopy(object):
    """Using canopy clustering to cluster.(canopy + Kmeans)

    Params:
    -------
    X : h5py file, ndarray, shape (n_sample, matrix(n, k)),
        The observations to cluster.

    namelist: [], dataset namelist of X h5py

    shape: (n_sample, timeSteps, features)

    T1: float64, distance Threshold in cheap distance func

    T2: float64, distance Threshold in cheap distance func, T1 > T2

    cheap_dis : cheap distance to determine canopy

    dis: expensive distance to cluster in the canopy
        The function of distance between diffierent samples

    canopies: list, all canpoies and the data in canopy

    canopies_centers: list, the center of each canopy

    n_cluster: the number of cluster, is same as length of canopies

    index: inverse index of each data, point out the canopy that belonged to

    Returns:
    --------
    link: https://dl.acm.org/citation.cfm?id=347123
    """
    def __init__(self, X, T1, T2, disfunc, max_iter=100):
        self.X = X
        self.T1 = T1
        self.T2 = T2
        self.disfunc = disfunc
        self.max_iter = max_iter

    def canopy(self):
        """ get canopy of all samples by cheap distance
        """
        data_list = self.X.namelist.copy()
        canopies = []
        canopy_centers = []
        index = [[] for i in range(self.X.number)]
        dis_matrix = get_dis_matrix(self.X, self.disfunc, cheap=True)
    
        while data_list:
            print('Name of X: ' + data_list[0])
            x = np.zeros(self.X.shape)
            self.X.get_sample_by_name(data_list[0], x)
            canopy_centers.append(x)
            row = name2id(data_list[0])
            # get sample where its distance to x < T1
            new_canopy = [data_list[0]]
            i = 0
            del data_list[0]
            t2_num = 0
            while i != len(data_list):
                col = name2id(data_list[i])
                dis = dis_matrix[row][col]
                # print('Y is {}, and dis = {}'.format(data_list[i], dis))
                nextFlag = True
                if dis <= self.T1:
                    new_canopy.append(data_list[i])
                    sample = int(data_list[i][3:])
                    index[sample].append(len(canopies))
                    if dis <= self.T2:
                        t2_num += 1
                        del data_list[i]
                        nextFlag = False
                if nextFlag is True:
                    i += 1
            print('size of canopy is {}\nNumber in T2 is {}'.format(len(new_canopy), t2_num))
            canopies.append(new_canopy)
        self.canopies = canopies
        self.canopy_centers = canopy_centers
        self.n_cluster = len(canopies)
        self.index = index
    
    def get_canopy(self):
        return self.canopies, self.index


    def prototypes(self):
        centroids = []
        self.label = [-1 for i in range(self.X.number)]
        self.dis = [sys.float_info.max for i in range(self.X.number)]
        for i, canopy in enumerate(self.canopies):
            tmp = np.random.randint(0, len(canopy))
            c = self.canopies[i][tmp]
            centroid = np.zeros(self.X.shape)
            self.X.get_sample_by_name(c, centroid)
            self.label[name2id(c)] = i
            centroids.append(centroid)
        self.centroids = centroids

    def readOneCanopy(self, canopy, x):
        for i, name in enumerate(canopy):
            self.X.get_sample_by_name(name, x[i])
    
    def em_clustering(self):
        t = 0
        cluster_number = len(self.centroids)
        cluster = [0 for i in range(len(self.centroids))]
        new_centroids = np.zeros((cluster_number,) + self.X.shape)
        canopy_sample = np.zeros((self.X.batchSize,) +  self.X.shape)

        while t < self.max_iter:
            t += 1
            flag = True
            # visit all canopy
            for i, canopy in enumerate(self.canopy_centers):
                self.readOneCanopy(self.canopies[i], canopy_sample)
                # visit all cluster center
                for cluster_label, centroid in enumerate(self.centroids):
                    if self.disfunc(centroid, self.canopy_centers[i], cheap=True) < self.T1:
                        for _idx, name in enumerate(canopy):
                            dis = self.disfunc(centroid, canopy_sample[_idx])
                            st_id = name2id(name)
                            if dis < self.dis[st_id]:
                                self.dis[st_id] = dis
                                self.label[st_id] = cluster_label
                                flag = False
                # update centroids
                for _idx, name in enumerate(self.canopy_centers):
                    st_id = name2id(name)
                    new_centroids[self.label[st_id]] += canopy_sample[st_id]
                    cluster[self.label[st_id]] += 1
            # update all centroids
            for i in range(cluster_number):
                self.centroids[i] = new_centroids[i] / cluster[i]
                new_centroids = 0
            if flag:
                break

    def fit(self):
        self.canopy()
        # self.prototypes()
        # self.em_clustering()
        return self.label
