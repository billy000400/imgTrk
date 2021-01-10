# This script's purpose is to train a preliminary CNN for tracking by Keras
# Author: Billy Li
# Email: li000400@umn.edu

# import starts
import sys
from pathlib import Path
import csv
import random
import pickle

import numpy as np

import tensorflow as tf
from tensorflow.keras import Model, initializers, regularizers
from tensorflow.keras.layers import(
    Input,
    Dense,
    Conv2D,
    BatchNormalization,
    MaxPool2D,Dropout,
    Flatten,
    TimeDistributed,
    Embedding,
    Reshape,
    Softmax
)
from tensorflow.keras.optimizers import Adam

import MyUnet

util_dir = Path.cwd().parent.joinpath('util')
sys.path.insert(1, str(util_dir))
from Config import extractor_config as Config
from mu2e_output import *
from Loss import unmasked_cce
from Metric import *
### import ends

def photographic_train(C):
    pstage("Start Training")

    ### load inputs
    pinfo('Loading processed arrays')
    X = np.load(C.X_npy)
    Y = np.load(C.Y_npy)

    pinfo('Standarlizing input arrays')
    mean = X.mean()
    std = X.std()
    std_inv = 1/std
    X = (X-mean)*std_inv



    ### outputs
    pinfo('Configuring output paths')
    cwd = Path.cwd()
    data_dir = cwd.parent.parent.joinpath('data')
    weights_dir = cwd.parent.parent.joinpath('weights')

    model_weights = weights_dir.joinpath(C.model_name+'.h5')
    record_file = data_dir.joinpath(C.record_name+'.csv')

    ### prepare model

    input_shape = (X.shape[1], X.shape[2], 1)
    architecture = MyUnet.U_Net(input_shape=input_shape, num_class=3)
    model = architecture.get_model()
    print(model.summary())

    # setup loss
    cce = unmasked_cce

    # setup metric
    ca = unmasked_categorical_accuracy

    # setup optimizer
    adam = Adam(1e-4)

    # setup callback
    CsvCallback = tf.keras.callbacks.CSVLogger(str(record_file), separator=",", append=False)
    LRCallback = tf.keras.callbacks.ReduceLROnPlateau(
        monitor='loss', factor=0.1, patience=2, verbose=0, mode='auto',
        min_delta=1e-3, cooldown=0, min_lr=1e-7
    )
    # print(cnn.summary())
    model.compile(optimizer=adam,\
                metrics = ca,\
                loss=cce)

    model.fit(x=X, y=Y,\
            validation_split=0.2,\
            shuffle=True,\
            batch_size=1, epochs=20,\
            callbacks = [CsvCallback, LRCallback])

    model.save(model_weights)

    pcheck_point('Finished Training')
    return C


if __name__ == "__main__":
    pbanner()
    psystem('Photographic track extractor')
    pmode('Testing Feasibility')
    pinfo('Input DType for testing: StrawDigiMC')

    # load pickle
    cwd = Path.cwd()
    pickle_path = cwd.joinpath('photographic.train.config.pickle')
    C = pickle.load(open(pickle_path,'rb'))

    # initialize parameters
    model_name = "photographic_UNet_00"
    record_name = "photographic_UNet_00"

    # setup parameters
    C.set_outputs(model_name, record_name)
    photographic_train(C)
