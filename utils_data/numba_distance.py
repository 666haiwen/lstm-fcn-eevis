from collections import defaultdict
from fastdtw import fastdtw
from pysptk.sptk import lpc
from numba import jit
import numpy as np
from numpy import linalg as la


@jit(nopython=True, parallel=True)
def euclidean(x, y, norm=2):
    """ calculate distance between matrix x and y by euclidean distance

    Params:
        x, y: ndarray (time_steps, feature_numbers)
        norm: int

    Returns:
        res: ndarray (feature_numbers,)
    """
    shape = x.shape
    res = np.zeros(shape[1])
    for col in range(shape[1]):
        if norm == 1:
            res[col] = np.sum(np.abs(x[:, col] - y[:, col]))
        else:
            res[col] = (np.sum((x[:, col] - y[:, col])**norm))**(1/norm)
    return np.mean(res)


def related(x, y, d_type=2, beta=1.5):
    """ calculate distance between matrix x and y by
        Pearson's correlation coefficient and related distances

    Params:
        x, y: ndarray (time_steps, feature_numbers)
        d_type: 1 means d1 and 2 means d2
        beta: using for d1
        resType: value or vector, decided the return type

    Returns:
        res: ndarray (feature_numbers,)
    """
    shape = x.shape
    res = np.zeros(shape[1])
    for col in range(shape[1]):
        cc = np.corrcoef(x[:, col], y[:, col])[0][1]
        res[col] = ((1 - cc) / (1 + cc))**beta if d_type == 1 else 2*(1 - cc)
    return np.mean(res)


@jit(nopython=True, parallal=True)
def sts(x, y):
    """ calculate distance between matrix x and y by short time series distance

    Params:
        x, y: ndarray (time_steps, feature_numbers)

    Returns:
        res: ndarray (feature_numbers,)
    """
    shape = x.shape
    res = np.zeros(shape[1])
    dis_time = 20 / 2000    # 20s --> 2001 steps
    for col in range(shape[1]):
        res[col] = np.sum((x[1:, col] - x[:-1, col] - y[1:, col] + y[:-1, col])**2)
        res[col] = np.sqrt(res[col]) / dis_time
    return np.mean(res)


@jit(nopython=True, parallal=True)
def dtw(x, y):
    """ calculate distance between matrix x and y by Dynamic time warping

    Params:
        x, y: ndarray (time_steps, feature_numbers)

    Returns:
        res: ndarray (feature_numbers,)
    """
    return euclidean(x, y, norm=1)
    shape = x.shape
    res = np.zeros(shape[1])
    for col in range(shape[1]):
        res[col] = fastdtw(x[:, col], y[:, col])[0]
    return np.mean(res)


@jit(nopython=True, parallal=True)
def kullback_Liebler(x, y, s=20):
    """ calculate distance between matrix x and y by
        transition probabilities of two Markov chains

    Params:
        x, y: ndarray (time_steps, feature_numbers)
        s: probability distribution numbers

    Returns:
        res: ndarray (feature_numbers,)
    """
    shape = x.shape
    res = np.zeros(shape[1])
    p1 = np.zeros((s, s))
    p2 = np.zeros((s, s))
    for col in range(shape[1]):
        min_v = min(np.min(x[:, col]), np.min(y[:, col]))
        max_v = max(np.max(x[:, col]), np.max(y[:, col]))
        bin_width = (max_v - min_v) / s
        if bin_width == 0:
            tmp_x = x[:, col] - min_v
            tmp_y = y[:, col] - min_v
        else:
            tmp_x = (x[:, col] - min_v) / bin_width
            tmp_y = (y[:, col] - min_v) / bin_width
        for i in range(shape[0] - 1):
            a = int(tmp_x[i]) if tmp_x[i] < s else s - 1
            b = int(tmp_x[i + 1]) if tmp_x[i + 1] < s else s - 1
            p1[a][b] += 1
            a = int(tmp_y[i]) if tmp_y[i] < s else s - 1
            b = int(tmp_y[i + 1]) if tmp_y[i + 1] < s else s - 1
            p2[a][b] += 1
        for i in range(s):
            if np.sum(p1[i, :] != 0):
                p1[i, :] /= np.sum(p1[i, :])
            if np.sum(p2[i, :] != 0):
                p2[i, :] /= np.sum(p2[i, :])
        for i in range(s):
            d = 0
            for j in range(s):
                if p1[i][j] == 0 or p2[i][j] == 0:
                    continue
                log = np.log(p1[i][j]) - np.log(p2[i][j])
                d += p1[i][j] * log
                d += p2[i][j] * log * (-1)
            res[col] += d / 2
        res[col] /= s
    return np.mean(res)


def autocorrelation_matrix(x):
    """ calculate autocorrelation coefficients of series k

     Params:
        x: ndarray (m, )

    Returns:
        res: ndarray(m, m)
    """
    shape = x.shape
    rr = np.zeros(shape)
    for lag in range(shape[0]):
        for t in range(shape[0] - lag):
            rr[lag] += x[t]*x[t + lag]
    res = np.zeros((shape[0], shape[0]))
    for row in range(shape[0]):
        for col in range(shape[0]):
            res[row][col] = rr[abs(row - col)]
    return res



def dis_in_fdtw(x, y, Ry):
    """ calculate distance between frame x and frame y

    Params:
        x, y: ndarray

    Returns:
        res: value of distance
    """
    return np.log(np.dot(np.dot(x, Ry), np.transpose(x)) / np.dot(np.dot(y, Ry), np.transpose(y)))


def frame_dtw(x, y, Rx, Ry, frame=20):
    """ calculate series x and y distance by dtw(frame not point)

    Params:
        x, y:   list, constructed by m frames, each frame is ndarry
        Rx, Ry: list, length = m, each frame is ndarray(k, k)

        
    Returns:
        vaule and path after dtw
        path is Correspondence between x and y
    """
    shape = x.shape
    start = 0
    batch = int(shape[0] / frame)
    window = []
    for i in range(frame):
        stop = start + batch
        window.append((start, stop))
        start = stop
    d = np.array([[abs(dis_in_fdtw(x[s_x[0]:s_x[1]], y[s_y[0]:s_y[1]], Ry[j])) \
        for j, s_y in enumerate(window)] for s_x in window])
    window = [(i + 1, j + 1) for i in range(frame) for j in range(frame)]
    D = defaultdict(lambda: (float('inf'),))
    D[0, 0] = (0, 0, 0)
    for i, j in window:
        dt = d[i-1, j-1]
        D[i, j] = min((D[i-1, j][0]+dt, i-1, j), (D[i, j-1][0]+dt, i, j-1),
                      (D[i-1, j-1][0]+dt, i-1, j-1), key=lambda a: a[0])
    _path = [0 for i in range(frame)]
    i, j = frame, frame
    while not i == j == 0:
        _path[i - 1] = j - 1
        i, j = D[i, j][1], D[i, j][2]
    return (D[frame, frame][0], _path)


def get_lpc_frameAndautocoeff(x, frame=20):
    """ get lpc vector of pattern x

    Parmas:
        x: ndarray
        frame: number of frame
    
    Returns:
        list: [frame], elemet is ndarray of lpc vector
    """
    shape = x.shape
    res = []
    Rx = []
    start = 0
    batch = int (shape[0] / frame)
    for i in range(frame):
        stop = start + batch
        res.append(lpc(np.copy(x[start:stop], order='C'), order=batch - 1))
        Rx.append(autocorrelation_matrix(x[start:stop]))
        start = stop
    return res, Rx


@jit(nopython=True)
def base_LPC(x, y, frame=20):
    """ calculate distance between matrix x and y by
    Dissimilarity between two spoken words

    Params:
        x, y: ndarray (time_steps, feature_numbers)

    Returns:
        res: ndarray (feature_numbers,)
    """
    # dtw time points correspond ok time series correspond??
    shape = x.shape
    res = np.zeros(shape[1])
    Rx = Ry = []
    for col in range(shape[1]):
        pattern_x, Rx = get_lpc_frameAndautocoeff(x[:, col])
        pattern_y, Ry = get_lpc_frameAndautocoeff(y[:, col])
        _, dtw_x2y = frame_dtw(x[:, col], y[:, col], Rx, Ry, frame)
        _, dtw_y2x = frame_dtw(y[:, col], x[:, col], Rx, Ry, frame)
        for i in range(frame):
            ay = pattern_y[dtw_x2y[i]]
            ax = pattern_x[i]
            res[col] += abs(np.log(np.dot(np.dot(np.transpose(ay), Rx[i]), ay) / np.dot(np.dot(np.transpose(ax), Rx[i]), ax)))
            ay_t = pattern_x[dtw_y2x[i]]
            ax_t = pattern_y[i]
            res[col] += abs(np.log(np.dot(np.dot(np.transpose(ay_t), Ry[i]), ay_t) / np.dot(np.dot(np.transpose(ax_t), Ry[i]), ax_t)))
        res[col] /= (2 * frame)
    return np.mean(res)


def pca_based(a, b):
    """ calculate distance between matrix x and y by pca_based

    link:https://www.researchgate.net/publication/221351631

    Params:
        x, y: ndarray (time_steps, feature_numbers)

    Returns:
        res: value of distance
    """
    a_cov = np.cov(a)
    b_cov = np.cov(b)
    _, sigma_a, va = la.svd(a_cov, full_matrices=False)
    _, sigma_b, vb = la.svd(b_cov, full_matrices=False)
    shape = va.shape
    w = np.zeros(shape[1])
    for i in range(shape[1]):
        w[i] = (sigma_a[i] + sigma_b[i]) / 2
    w /= np.sum(w)
    res = 0
    for i in range(shape[1]):
        res += w[i] * abs(np.dot(va[:, i], vb[:, i]))
    return res
