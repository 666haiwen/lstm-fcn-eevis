from keras.utils import plot_model
import os.path as osp, os
import sys
sys.path.extend([osp.dirname(__file__),
                 osp.join(osp.dirname(__file__), "utils_data")])

from model import generate_model
from train_eval import evaluate_model, train_model
# os.environ['CUDA_VISIBLE_DEVICES'] = '0' 

if __name__ == '__main__':
    m = generate_model()
    # plot_model(m, to_file='model.png', show_shapes=True)
    train_model(m)
    # evaluate_model(m)
