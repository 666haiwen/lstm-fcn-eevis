import sys
import random
import time
import h5py
import numpy as np


def nearest_center(u, centers, distance):
    """Find the nearest center to the point u.
    
    Params:
    -------
        u: the maxtrix of one sample
        centers: ndarray, shape(n_cluster, timeSteps, features)
        distance: function of distance between two samples
    
    Returns:
    --------
        A center id indicating the nearest center to the sample u.
    """
    d = distance(u, centers[0])
    label = 0
    for i in range(1, len(centers)):
        tmp = distance(u, centers[i])
        if tmp < d:
            d = tmp
            label = i
    return label


def init_k(X, namelist, shape, n_cluster, distance):
    """Using k-means++ to initialize the cluster center

    Params:
    -------

    Returns:
    cluster: the points of each cluster, list, shape(n_cluster, cluster_number)
    centorids: the center of each cluster, shape(n_cluster, matrix(n, k))
    """
    n_sample = shape[0]
    cluster = [[random.randrange(0, n_sample - 1)]]
    samples = [-1 for i in range(n_sample)]
    centroids = np.zeros((n_cluster, shape[1], shape[2]))
    centroids[0] = X[namelist[cluster[0][0]]][:]
    X[namelist[cluster[0][0]]].read_direct(centroids[0])
    x = np.zeros((shape[1], shape[2]))
    y = np.zeros((shape[1], shape[2]))
    dis = [sys.float_info.max for i in range(n_sample)]
    center = [0]
    new_center = 0
    while len(cluster) < n_cluster:
        d = 0
        new_center = 0
        print(len(cluster))
        X[namelist[new_center]].read_direct(y)
        for i in range(n_sample):
            if i in center:
                continue
            X[namelist[i]].read_direct(x)
            dis[i] = min(dis[i], distance(x, y))
            if dis[i] > d:
                d = dis[i]
                new_center = i
        center.append(new_center)
        cluster.append([new_center])
        samples[new_center] = len(cluster)
        X[namelist[new_center]].read_direct(centroids[len(cluster)])
    return cluster, centroids, samples


def kmeans(X, namelist, shape, distance, n_cluster=100, max_iter=200):
    """K-means clustering algorithm.
    Get k-means results of matrix sample and the initilization is k-means++

    Parameters
    ----------
    X : h5py file, ndarray, shape (n_sample, matrix(n, k)),
        The observations to cluster.

    namelist: [], dataset namelist of X h5py

    shape: (n_sample, timeSteps, features)

    n_clusters : int, default is 100
        The number of clusters to form as well as the number of
        centroids to generate.
    
    distance : func
        The function of distance between diffierent samples

    max_iter : int, optional, default 300
        Maximum number of iterations of the k-means algorithm to run.

    Returns:
    --------
    samples: list, lable of each sample
    centroids: the center of each cluster, shape(n_cluster, matrix(n, k))
    """
    n_sample = shape[0]
    print('Begin Kmeans cluster by distance func ' + distance.__name__)
    cluster, centroids, samples = init_k(X, namelist, shape, n_cluster, distance)
    x = np.zeros((shape[1], shape[2]))
    for times in range(max_iter):
        print('epoch: {}s\nTimes cost:'.format(times))
        beforeTime = time.time()
        changeCluster = False
        cluster = [[] for i in range(n_cluster)]
        for i in range(n_sample):
            X[namelist[i]].read_direct(x)
            update_label = nearest_center(x, centroids, distance)
            cluster[update_label].append(i)
            if update_label != samples[i]:
                samples[i] = update_label
                changeCluster = True
        if not changeCluster:
            break
        # update centroids and clusters
        for i in range(n_cluster):
            centroids[i] = 0
            for v in cluster[i]:
                centroids[i] += X[namelist[v]]
            centroids /= len(cluster[i])
        afterTime = time.time()
        print('{}s'.format(afterTime - beforeTime))
    return samples, centroids
