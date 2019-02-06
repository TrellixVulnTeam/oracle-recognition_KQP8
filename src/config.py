from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from easydict import EasyDict


# Auto-generate version
def _auto_version(c):
  _version = c['DATABASE_NAME']
  if c['WITH_REC']:
    _version += '_{}_{}'.format(c['DECODER_TYPE'], c['REC_LOSS'])
  else:
   _version += '_no_rec'
  if c['DPP_TEST_AS_VALID']:
    _version += '_tav'
  return _version


__C = EasyDict()


# ===========================================
# #             Hyperparameters             #
# ===========================================

# Database name
# 'radical': Oracle Radicals
# 'mnist': MNIST
# 'cifar10' CIFAR-10
__C.DATABASE_NAME = 'radical'
# __C.DATABASE_NAME = 'mnist'
__C.DATABASE_MODE = 'small'

# Training version
# Set None to auto generate version
__C.VERSION = None

# Learning rate
__C.LEARNING_RATE = 0.001

# Learning rate with exponential decay
# Use learning rate decay
__C.LR_DECAY = True
# Decay steps
__C.LR_DECAY_STEPS = 2000
# Exponential decay rate
__C.LR_DECAY_RATE = 0.96

# Epochs
__C.EPOCHS = 20

# Batch size
__C.BATCH_SIZE = 512


# ===========================================
# #               Preprocessing             #
# ===========================================

# Setting test set as validation when preprocessing data
__C.DPP_TEST_AS_VALID = True

# Rate of train-test split
__C.TEST_SIZE = 0.2

# Rate of train-validation split
__C.VALID_SIZE = 0.1

# Resize images
__C.RESIZE_INPUTS = False
# Input size
__C.INPUT_SIZE = (56, 56)

# Resize images
__C.RESIZE_IMAGES = True
# Image size
__C.IMAGE_SIZE = (56, 56)

# Using data augment
__C.USE_DATA_AUG = True
# Parameters for data augment
__C.DATA_AUG_PARAM = dict(
    rotation_range=40,
    width_shift_range=0.4,
    height_shift_range=0.4,
    # shear_range=0.1,
    zoom_range=[1.0, 2.0],
    horizontal_flip=True,
    fill_mode='nearest'
)
# Keep original images if use data augment
__C.DATA_AUG_KEEP_SOURCE = True
# The max number of images of a class if use data augment
__C.MAX_IMAGE_NUM = 2000

# Oracle Parameters
# Number of radicals to use for training
# Max = 148
__C.NUM_RADICALS = 148

# Preprocessing images of superpositions of multi-objects
# If None, one image only shows one object.
# If n, one image includes a superposition of n objects, the positions of
# those objects are random.
__C.NUM_MULTI_OBJECT = 2
# The number of multi-objects images
__C.NUM_MULTI_IMG = 10000
# If overlap, the multi-objects will be overlapped in a image.
__C.OVERLAP = False
# If Repeat, repetitive labels will appear in a image.
__C.REPEAT = False


# ===========================================
# #            Model Architecture           #
# ===========================================

# -------------------------------------------
# Classification

# Classification loss
# 'margin': margin loss
# 'margin_h': margin loss in Hinton's paper
__C.CLF_LOSS = 'margin_h'

# Parameters of margin loss
# default: {'m_plus': 0.9, 'm_minus': 0.1, 'lambda_': 0.5}
__C.MARGIN_LOSS_PARAMS = {'m_plus': 0.9,
                          'm_minus': 0.1,
                          'lambda_': 0.5}
# default: {'margin': 0.4, 'down_weight': 0.5}
__C.MARGIN_LOSS_H_PARAMS = {'margin': 0.4,
                            'down_weight': 0.5}

# Add epsilon(a very small number) to zeros
__C.EPSILON = 1e-9

# stddev of tf.truncated_normal_initializer()
__C.WEIGHTS_STDDEV = 0.01

# -------------------------------------------
# Optimizer and learning rate decay

# Optimizer
# 'gd': GradientDescentOptimizer()
# 'adam': AdamOptimizer()
# 'momentum': MomentumOptimizer()
__C.OPTIMIZER = 'adam'

# Momentum Optimizer
# Boundaries of learning rate
__C.LR_BOUNDARIES = [82, 123, 300]
# Stage of learning rate
__C.LR_STAGE = [1, 0.1, 0.01, 0.002]
# Momentum parameter of momentum optimizer
__C.MOMENTUM = 0.9

# -------------------------------------------
# Reconstruction

# Training with reconstruction
__C.WITH_REC = True

# Type of decoder of reconstruction:
# 'fc': full_connected layers
# 'conv': convolution layers
# 'conv_t': transpose convolution layers
__C.DECODER_TYPE = 'conv_t'

# Reconstruction loss
# 'mse': Mean Square Error
# 'ce' : sigmoid_cross_entropy_with_logits
__C.REC_LOSS = 'mse'

# Scaling for reconstruction loss
__C.REC_LOSS_SCALE = 0.392  # 0.0005*32*32=0.512  # 0.0005*784=0.392

# -------------------------------------------
# Transfer Learning

# Transfer learning mode
__C.TRANSFER_LEARNING = 'encode'  # None

# Transfer learning model
# 'vgg16', 'vgg19', 'resnet50', 'inceptionv3', 'xception'
__C.TL_MODEL = 'xception'

# Pooling method: 'avg', None
__C.BF_POOLING = None


# ===========================================
# #         Training Configurations         #
# ===========================================

# Display step
# Set None to not display details
__C.DISPLAY_STEP = None  # batches

# Save summary step
# Set None to not save summaries
__C.SAVE_LOG_STEP = 100  # batches

# Save reconstructed images
# Set None to not save images
__C.SAVE_IMAGE_STEP = 100  # batches

# Maximum images number in a col
__C.MAX_IMAGE_IN_COL = 10

# Calculate train loss and valid loss using full data set
# 'per_epoch': evaluate on full set when n epochs finished
# 'per_batch': evaluate on full set when n batches finished
__C.FULL_SET_EVAL_MODE = 'per_epoch'
# None: not evaluate
__C.FULL_SET_EVAL_STEP = 1

# Save models
# 'per_epoch': save models when n epochs finished
# 'per_batch': save models when n batches finished
# __C.SAVE_MODEL_MODE = None
__C.SAVE_MODEL_MODE = 'per_epoch'
# None: not save models
__C.SAVE_MODEL_STEP = 5
# Maximum number of recent checkpoints to keep.
__C.MAX_TO_KEEP_CKP = 3

# Calculate the train loss of full data set, which may take lots of time.
__C.EVAL_WITH_FULL_TRAIN_SET = False

# Show details of training progress
__C.SHOW_TRAINING_DETAILS = False

# -------------------------------------------
# Test
# 'after_training': evaluate after all training finished
# 'per_epoch': evaluate when a epoch finished
# None: Do not test

# Evaluate on single-object test set
__C.TEST_SO_MODE = 'per_epoch'

# Evaluate on multi-objects test set
__C.TEST_MO_MODE = 'per_epoch'

# Evaluate on Oracles test set after
__C.TEST_ORACLE_MODE = 'per_epoch'


# ===========================================
# #          Testing Configurations         #
# ===========================================

# Testing version name
__C.TEST_VERSION = __C.VERSION

# Testing checkpoint index
# If None, load the latest checkpoint.
__C.TEST_CKP_IDX = None

# Testing with reconstruction
__C.TEST_WITH_REC = True

# Saving testing reconstruction images
# If None, do not save images.
__C.TEST_SAVE_IMAGE_STEP = 5  # batches

# Batch size of testing
# should be same as training batch_size
__C.TEST_BATCH_SIZE = __C.BATCH_SIZE

# -------------------------------------------
# Multi-objects detection

# Label for generating reconstruction images
# 'pred': Use predicted y
# 'real': Use real labels y
__C.LABEL_FOR_TEST = 'pred'  # 'real'

# Mode of prediction for multi-objects detection
# 'top_n': sort vectors, select longest n classes as y
# 'length_rate': using length rate of the longest vector class as threshold
__C.MOD_PRED_MODE = 'top_n'  # 'length_rate'

# Max number of prediction y
__C.MOD_PRED_MAX_NUM = 2

# Threshold for 'length_rate' mode
__C.MOD_PRED_THRESHOLD = 0.5

# Save test prediction vectors
__C.SAVE_TEST_PRED = True


# ===========================================
# #                  Others                 #
# ===========================================

if __C.VERSION is None:
  __C.VERSION = _auto_version(__C)

# Source data directory path
__C.SOURCE_DATA_PATH = '../data/source_data'

# Preprocessed data path
__C.DPP_DATA_PATH = '../data/preprocessed_data'

# Oracle labels path
__C.ORAClE_LABEL_PATH = __C.SOURCE_DATA_PATH + '/recognized_oracles_labels.csv'

# Path for saving logs
__C.TRAIN_LOG_PATH = '../train_logs'

# Path for saving summaries
__C.SUMMARY_PATH = '../tf_logs'

# Path for saving models
__C.CHECKPOINT_PATH = '../checkpoints'

# Path for saving testing logs
__C.TEST_LOG_PATH = '../test_logs'


# ===========================================
# #        Multi-GPUs Configurations        #
# ===========================================

# Save trainable variables on CPU
__C.VAR_ON_CPU = True

# Number of GPUs
__C.GPU_NUMBER = 2

# Number of tasks
__C.TASK_NUMBER = 4

# The decay to use for the moving average.
# If None, not use
__C.MOVING_AVERAGE_DECAY = 0.9999

# ===========================================

# get config by: from config import config
config = __C
