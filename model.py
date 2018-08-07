from keras.layers import (LSTM, Activation, BatchNormalization, Conv1D, Dense,
                          Dropout, GlobalAveragePooling1D, Input, Masking,
                          Permute, Reshape, concatenate, multiply)
from keras.models import Model

from config import cfg


def squeeze_excite_block(input):
    ''' Create a squeeze-excite block
    Params
    ------
    `input`: input tensor

    Returns 
    -------
    a keras tensor
    '''
    filters = input._keras_shape[-1] # channel_axis = -1 for TF

    se = GlobalAveragePooling1D()(input)
    se = Reshape((1, filters))(se)
    se = Dense(filters // cfg.MODEL.SE_RATIO,  activation='relu', kernel_initializer='he_normal', use_bias=False)(se)
    se = Dense(filters, activation='sigmoid', kernel_initializer='he_normal', use_bias=False)(se)
    se = multiply([input, se])
    return se


def generate_model():
    ip = Input(shape=(cfg.TIME_STEPS, cfg.FEATURES))

    x = Masking()(ip)
    x = LSTM(8)(x)
    x = Dropout(0.8)(x)

    #y = Permute((2, 1))(ip)
    y = ip
    y = Conv1D(128, 8, padding='same', kernel_initializer='he_uniform')(y)
    y = BatchNormalization()(y)
    y = Activation('relu')(y)
    y = squeeze_excite_block(y)

    y = Conv1D(256, 5, padding='same', kernel_initializer='he_uniform')(y)
    y = BatchNormalization()(y)
    y = Activation('relu')(y)
    y = squeeze_excite_block(y)

    y = Conv1D(128, 3, padding='same', kernel_initializer='he_uniform')(y)
    y = BatchNormalization()(y)
    y = Activation('relu')(y)

    y = GlobalAveragePooling1D()(y)

    x = concatenate([x, y])

    out = Dense(cfg.DATA.NUM_CLASSES, activation='softmax')(x)

    model = Model(ip, out)
    model.summary()

    # add load model code here to fine-tune

    return model

def generate_attention_model():
    ip = Input(shape=(cfg.TIME_STEPS, cfg.FEATURES))

    ''' sabsample timesteps to prevent OOM due to Attention LSTM '''
    stride = 3

    x = Permute((2, 1))(ip)
    x = Conv1D(cfg.FEATURES // stride, 8, strides=stride, padding='same', activation='relu', use_bias=False,
               kernel_initializer='he_uniform')(x) # (None, variables / stride, timesteps)

    x = Masking()(x)
    x = AttentionLSTM(384, unroll=True)(x)
    x = Dropout(0.8)(x)

    y = Permute((2, 1))(ip)
    y = Conv1D(128, 8, padding='same', kernel_initializer='he_uniform')(y)
    y = BatchNormalization()(y)
    y = Activation('relu')(y)
    y = squeeze_excite_block(y)

    y = Conv1D(256, 5, padding='same', kernel_initializer='he_uniform')(y)
    y = BatchNormalization()(y)
    y = Activation('relu')(y)
    y = squeeze_excite_block(y)

    y = Conv1D(128, 3, padding='same', kernel_initializer='he_uniform')(y)
    y = BatchNormalization()(y)
    y = Activation('relu')(y)

    y = GlobalAveragePooling1D()(y)

    x = concatenate([x, y])

    out = Dense(cfg.DATA.NUM_CLASSES, activation='softmax')(x)

    model = Model(ip, out)
    model.summary()

    # add load model code here to fine-tune

    return model



if __name__ == "__main__":
    model = generate_model()
    