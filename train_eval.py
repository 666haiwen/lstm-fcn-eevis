from __future__ import absolute_import, division, print_function

import os
import warnings

import numpy as np
from keras import backend as K
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, TensorBoard

from keras.layers import Permute
from keras.models import Model, load_model
from keras.optimizers import Adam
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical

from config import cfg
from utils_data.generate_data import DataLoader
from sklearn.preprocessing import LabelEncoder

warnings.simplefilter('ignore', category=DeprecationWarning)


def multi_label_log_loss(y_pred, y_true):
    return K.sum(K.binary_crossentropy(y_pred, y_true), axis=-1)


def _average_gradient_norm(model, X_train, y_train, batch_size):
    # just checking if the model was already compiled
    if not hasattr(model, "train_function"):
        raise RuntimeError("You must compile your model before using it.")

    weights = model.trainable_weights  # weight tensors

    get_gradients = model.optimizer.get_gradients(model.total_loss, weights)  # gradient tensors

    input_tensors = [
        # input data
        model.inputs[0],
        # how much to weight each sample by
        model.sample_weights[0],
        # labels
        model.targets[0],
        # train or test mode
        K.learning_phase()
    ]

    grad_fct = K.function(inputs=input_tensors, outputs=get_gradients)

    steps = 0
    total_norm = 0
    s_w = None

    nb_steps = X_train.shape[0] // batch_size

    if X_train.shape[0] % batch_size == 0:
        pad_last = False
    else:
        pad_last = True

    def generator(X_train, y_train, pad_last):
        for i in range(nb_steps):
            X = X_train[i * batch_size: (i + 1) * batch_size, ...]
            y = y_train[i * batch_size: (i + 1) * batch_size, ...]

            yield (X, y)

        if pad_last:
            X = X_train[nb_steps * batch_size:, ...]
            y = y_train[nb_steps * batch_size:, ...]

            yield (X, y)

    datagen = generator(X_train, y_train, pad_last)

    while steps < nb_steps:
        X, y = next(datagen)
        # set sample weights to one
        # for every input
        if s_w is None:
            s_w = np.ones(X.shape[0])

        gradients = grad_fct([X, s_w, y, 0])
        total_norm += np.sqrt(np.sum([np.sum(np.square(g)) for g in gradients]))
        steps += 1

    if pad_last:
        X, y = next(datagen)
        # set sample weights to one
        # for every input
        if s_w is None:
            s_w = np.ones(X.shape[0])

        gradients = grad_fct([X, s_w, y, 0])
        total_norm += np.sqrt(np.sum([np.sum(np.square(g)) for g in gradients]))
        steps += 1

    return total_norm / float(steps)



def train_model(model, 
                monitor='val_acc', 
                optimization_mode='max', 
                compile_model=True):
    data_loader = DataLoader(seed=cfg.DATA.SPLIT_SEED, weights='default', verbose=True)
    # load all data into memory
    X_train, y_train = data_loader.data_read('train')
    X_validation, y_validation = data_loader.data_read('validation')
    # factor = 1. / np.cbrt(2)
    factor = 1. / 2

    if not os.path.exists(cfg.MODEL.SAVE_PATH):
        os.makedirs(cfg.MODEL.SAVE_PATH)

    weight_fn = os.path.join(cfg.MODEL.SAVE_PATH, "14k_renormalization_no_zeroFilling_%s_sampling_weights.h5" % cfg.DATA.PREFIX)
    if os.path.exists(weight_fn):
        model.load_weights(weight_fn)
        # model = load_model(weight_fn)

    model_checkpoint = ModelCheckpoint(weight_fn, verbose=1, mode=optimization_mode,
                                       monitor=monitor, save_best_only=True, save_weights_only=False)
    reduce_lr = ReduceLROnPlateau(monitor=monitor, patience=10, mode=optimization_mode,
                                  factor=factor, cooldown=0, min_lr=cfg.TRAIN.MIN_LR, verbose=2)

    tb_cb = TensorBoard(log_dir=cfg.MODEL.LOG_PATH, batch_size=cfg.TRAIN.BATCH_SIZE)

    optm = Adam(lr=cfg.TRAIN.LR)

    if compile_model:
        model.compile(optimizer=optm, loss='categorical_crossentropy', metrics=['accuracy'])

    callback_list = [model_checkpoint, reduce_lr, tb_cb]
    # load all data into memory and fit
    model.fit(X_train, y_train, epochs=cfg.TRAIN.EPOCHS,
                        verbose=1,
                        validation_data=(X_validation, y_validation),
                        class_weight=data_loader.class_weights,
                        callbacks=callback_list)
    # load data by batches
    # steps_per_epoch = int(1.0 * data_loader.train.num_of_paths / cfg.TRAIN.BATCH_SIZE)
    # val_steps_per_epoch = int(1.0 * data_loader.val.num_of_paths / cfg.TRAIN.BATCH_SIZE)

    # model.fit_generator(data_loader.generator('train', cfg.TRAIN.BATCH_SIZE), 
    #                     epochs=cfg.TRAIN.EPOCHS,
    #                     steps_per_epoch=steps_per_epoch,
    #                     verbose=1,
    #                     validation_data=data_loader.generator('validation', cfg.TRAIN.BATCH_SIZE),
    #                     validation_steps=val_steps_per_epoch,
    #                     class_weight=data_loader.class_weights,
    #                     callbacks=callback_list,
    #                     workers=cfg.TRAIN.WORKERS,
    #                     max_queue_size=cfg.TRAIN.MAX_QUEUE_SIZE)
    


def evaluate_model(model):
    data_loader = DataLoader(seed=cfg.DATA.SPLIT_SEED, weights='default', verbose=True)
    # load all data into memory
    x, y = data_loader.data_read(tag='test', seed=cfg.DATA.SPLIT_SEED)

    optm = Adam(lr=cfg.TRAIN.LR)
    model.compile(optimizer=optm, loss='categorical_crossentropy', metrics=['accuracy'])

    weight_fn = os.path.join(cfg.MODEL.SAVE_PATH, "14k_renormalization_no_zeroFilling_%s_sampling_weights.h5" % cfg.DATA.PREFIX)
    model.load_weights(weight_fn)

    print("\nEvaluating : ")
    steps = int(1.0 * data_loader.test.num_of_paths / cfg.TEST.BATCH_SIZE)
    # load all data into memeory and get result
    loss, accuracy = model.evaluate(x, y, batch_size=cfg.TEST.BATCH_SIZE)
    # test by batches
    # loss, accuracy = model.evaluate_generator(data_loader.generator('test', cfg.TEST.BATCH_SIZE),
    #                                           steps=steps, workers=cfg.TEST.WORKERS,
    #                                           max_queue_size=cfg.TEST.MAX_QUEUE_SIZE)
    
    print()
    print("Final Accuracy : ", accuracy)

    return accuracy, loss

def set_trainable(layer, value):
   layer.trainable = value

   # case: container
   if hasattr(layer, 'layers'):
       for l in layer.layers:
           set_trainable(l, value)

   # case: wrapper (which is a case not covered by the PR)
   if hasattr(layer, 'layer'):
        set_trainable(layer.layer, value)


def compute_average_gradient_norm(model, 
                                  dataset_fold_id=None, 
                                  cutoff=None, 
                                  normalize_timeseries=False):
    data_loader = DataLoader(seed=cfg.DATA.SPLIT_SEED, weights='default')

    optm = Adam(lr=cfg.TRAIN.LR)
    model.compile(optimizer=optm, loss='categorical_crossentropy', metrics=['accuracy'])

    average_gradient = _average_gradient_norm(model, X_train, y_train, cfg.TRAIN.BATCH_SIZE)
    print("Average gradient norm : ", average_gradient)


class MaskablePermute(Permute):

    def __init__(self, dims, **kwargs):
        super(MaskablePermute, self).__init__(dims, **kwargs)
        self.supports_masking = True


def f1_score(y_true, y_pred):
    def recall(y_true, y_pred):
        """Recall metric.

        Only computes a batch-wise average of recall.

        Computes the recall, a metric for multi-label classification of
        how many relevant items are selected.
        """
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        recall = true_positives / (possible_positives + K.epsilon())
        return recall

    def precision(y_true, y_pred):
        """Precision metric.

        Only computes a batch-wise average of precision.

        Computes the precision, a metric for multi-label classification of
        how many selected items are relevant.
        """
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        precision = true_positives / (predicted_positives + K.epsilon())
        return precision

    precision = precision(y_true, y_pred)
    recall = recall(y_true, y_pred)

    return 2 * ((precision * recall) / (precision + recall))
