import h5py
from random import random
import numpy as np


def nearest_W(u, W, distance):
    """Find the nearest unit to the point u.

    Params:
    -------
        u: the maxtrix of one sample
        W: An array of centers' indices
        distance: function of distance between two samples

    Returns:
    --------
        A center id indicating the nearest center to the sample u.
    """
    d = distance(u, W[0], resType='value')
    label = 0
    for i in range(1, len(W)):
        tmp = distance(u, W[i], resType='value')
        if tmp < d:
            d = tmp
            label = i
    return label


def initW(X, namelist, shape, n_cluster):
    """Using k-means++ to initialize the cluster center

    Params:
    -------

    Returns:
    W: the init matrix of each unit, ndarray, shape(n_cluster, shape[1], shape[2])
    samples: the label of each sample, shape(n_cluster, matrix(n, k))
    """
    W = np.random.random((n_cluster, shape[1], shape[2])) * 0.1
    base = np.zeros((shape[1], shape[2]))
    samples = [-1 for i in range(shape[0])]
    for i in namelist:
        base += X[i]
    base /= shape[0]
    for i in n_cluster:
        W[i] += base
    return W, samples


def som(X, namelist, shape, distance, n_cluster=100, max_iter=200):
    """SOM(Self-Organizing Maps) clustering algorithm.
    Get SOM results of matrix sample and the initializtion of W is random based on samples

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

    max_iter : int, optional, default 200
        Maximum number of iterations of the k-means algorithm to run.

    Returns:
    --------
    samples: list, lable of each sample
    centroids: the center of each cluster, shape(n_cluster, matrix(n, k))
    """
    W, samples = initW(X, namelist, shape, n_cluster)
    T = 0
    while T < max_iter:
        rate = max(np.exp(-T), 1e-5) / np.sqrt(T + 9)
        for i, name in enumerate(namelist):
            updateW = nearest_W(X[name], W, distance)
            W[updateW] += rate * (X[name] - W[updateW])
            samples[i] = updateW
    cluster = [[] for i in range(n_cluster)]
    for i, label in enumerate(samples):
        cluster[i].append(label)
    return cluster, samples
