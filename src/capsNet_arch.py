from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from models.layers import *
from models.capsule_layers import *


def conv_block(model, cfg, conv_size, conv_stride, conv_depth,
               conv_padding='VALID', act_fn='relu', use_max_pool=False,
               pool_size=None, pool_strides=None, pool_padding='VALID',
               use_batch_norm=False, is_training=None, idx=0):

  model.add(ConvLayer(
      cfg,
      kernel_size=conv_size,
      stride=conv_stride,
      n_kernel=conv_depth,
      padding=conv_padding,
      act_fn=None if use_batch_norm else act_fn,
      idx=idx
  ))
  if use_max_pool:
    model.add(MaxPool(
        cfg,
        pool_size=pool_size,
        strides=pool_strides,
        padding=pool_padding,
        idx=idx
    ))
  if use_batch_norm:
    model.add(BatchNorm(
        cfg,
        is_training=is_training,
        momentum=0.99,
        act_fn=act_fn,
        idx=idx))


def classifier(inputs, cfg, batch_size=None, is_training=None):

  if cfg.DATABASE_NAME == 'radical':
    num_classes = cfg.NUM_RADICALS
  else:
    num_classes = 10

  model = Sequential(inputs)      # (b, 32, 32, 1)
  conv_block(
      model,
      cfg,
      conv_size=3,
      conv_stride=1,
      conv_depth=16,
      conv_padding='SAME',
      act_fn='relu',
      use_batch_norm=True,
      is_training=is_training,
      use_max_pool=True,
      pool_size=2,
      pool_strides=(2, 2),
      pool_padding='VALID',
      idx=0
  )                               # (b, 16, 16, 8)
  conv_block(
      model,
      cfg,
      conv_size=3,
      conv_stride=1,
      conv_depth=32,
      conv_padding='SAME',
      act_fn='relu',
      use_batch_norm=True,
      is_training=is_training,
      use_max_pool=True,
      pool_size=2,
      pool_strides=(2, 2),
      pool_padding='VALID',
      idx=1
  )                               # (b, 8, 8, 16)
  conv_block(
      model,
      cfg,
      conv_size=3,
      conv_stride=1,
      conv_depth=32,
      conv_padding='VALID',
      act_fn='relu',
      use_batch_norm=True,
      is_training=is_training,
      idx=2
  )                               # (b, 6, 6, 16)
  # conv_block(
  #     model,
  #     cfg,
  #     conv_size=3,
  #     conv_stride=2,
  #     conv_depth=32,
  #     conv_padding='VALID',
  #     act_fn='relu',
  #     use_batch_norm=True,
  #     route_epoch=10,
  #     kraining=is_training,
  #     idx=2
  # )                               # (b, 4, 4, 32)
  # models.add(Dense2Capsule(
  #     cfg,
  #     identity_map=True,
  #     num_caps=None,
  #     act_fn='relu',
  #     vec_dim=8,
  #     batch_size=batch_size
  # ))
  model.add(Conv2CapsLayer(
      cfg,
      kernel_size=3,
      stride=1,
      n_kernel=48,
      vec_dim=8,
      padding='VALID',
      batch_size=batch_size
  ))                               # (b, 4, 4, 32) -> (b, 216, 148, 16, 8)
  model.add(CapsLayer(
      cfg,
      num_caps=150,
      vec_dim=16,
      route_epoch=10,
      batch_size=batch_size,
      idx=0
  ))
  model.add(CapsLayer(
      cfg,
      num_caps=num_classes,
      vec_dim=32,
      route_epoch=10,
      batch_size=batch_size,
      idx=1
  ))

  return model.top_layer, model.info


def decoder(inputs, cfg, batch_size=None, is_training=None):

  model = Sequential(inputs)
  act_fn_last = None if cfg.REC_LOSS == 'ce' else 'relu'

  if cfg.DATABASE_NAME == 'radical':
    if cfg.DECODER_TYPE == 'fc':
      model.add(DenseLayer(
          cfg,
          out_dim=64,
          act_fn='relu',
          idx=0))
      # model.add(BatchNorm(
      #     cfg, is_training, momentum=0.99, act_fn='relu', idx=0))
      model.add(DenseLayer(
          cfg,
          out_dim=256,
          act_fn='relu',
          idx=1))
      # model.add(BatchNorm(
      #     cfg, is_training, momentum=0.99, act_fn='relu', idx=1))
      model.add(DenseLayer(
          cfg,
          out_dim=1024,
          act_fn=act_fn_last,
          idx=2))
      # model.add(BatchNorm(
      #     cfg, is_training, momentum=0.99, act_fn=act_fn_last, idx=2))
      assert model.top_layer.get_shape() == (
        batch_size, cfg.IMAGE_SIZE[0]*cfg.IMAGE_SIZE[1]
      ), model.top_layer.get_shape()

    elif cfg.DECODER_TYPE == 'conv':
      model.add(Reshape(      # (b, 4, 4, 1)
          (batch_size, 4, 4, -1), name='reshape'))
      model.add(ConvLayer(    # (b, 8, 8, 16)
          cfg,
          kernel_size=3,
          stride=1,
          n_kernel=16,
          resize=8,
          act_fn=None,
          idx=0))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn='relu', idx=0))
      model.add(ConvLayer(    # (b, 16, 16, 32)
          cfg,
          kernel_size=3,
          stride=1,
          n_kernel=32,
          resize=16,
          act_fn=None,
          idx=1))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn='relu', idx=1))
      model.add(ConvLayer(    # (b, 32, 32, 16)
          cfg,
          kernel_size=3,
          stride=1,
          n_kernel=16,
          resize=32,
          act_fn=None,
          idx=2))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn='relu', idx=2))
      model.add(ConvLayer(    # (b, 32, 32, 1)
          cfg,
          kernel_size=3,
          stride=1,
          n_kernel=1,
          resize=32,
          padding='SAME',
          act_fn=None,
          idx=3))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn=act_fn_last, idx=3))
      assert model.top_layer.get_shape() == (
        batch_size, *cfg.IMAGE_SIZE, 1), model.top_layer.get_shape()

    elif cfg.DECODER_TYPE == 'conv_t':
      model.add(Reshape(
          (batch_size, 1, 1, -1), name='reshape'))
      model.add(ConvTLayer(
          cfg,
          kernel_size=4,
          stride=1,
          n_kernel=16,
          output_shape=[batch_size, 4, 4, 16],
          padding='VALID',
          act_fn=None,
          idx=0))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn='relu', idx=0))
      model.add(ConvTLayer(
          cfg,
          kernel_size=9,
          stride=1,
          n_kernel=32,
          output_shape=[batch_size, 12, 12, 32],
          padding='VALID',
          act_fn=None,
          idx=1))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn='relu', idx=1))
      model.add(ConvTLayer(
          cfg,
          kernel_size=9,
          stride=1,
          n_kernel=16,
          output_shape=[batch_size, 20, 20, 16],
          padding='VALID',
          act_fn=None,
          idx=2))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn='relu', idx=2))
      model.add(ConvTLayer(
          cfg,
          kernel_size=9,
          stride=1,
          n_kernel=8,
          output_shape=[batch_size, 28, 28, 8],
          padding='VALID',
          act_fn=None,
          idx=3))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn='relu', idx=3))
      model.add(ConvTLayer(
          cfg,
          kernel_size=5,
          stride=1,
          n_kernel=1,
          output_shape=[batch_size, 32, 32, 1],
          padding='VALID',
          act_fn=None,
          idx=4))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn=act_fn_last, idx=4))
      assert model.top_layer.get_shape() == (
        batch_size, *cfg.IMAGE_SIZE, 1), model.top_layer.get_shape()

    else:
      raise ValueError('Wrong decoder type!')

  elif cfg.DATABASE_NAME == 'mnist':
    if cfg.DECODER_TYPE == 'fc':
      model.add(DenseLayer(
          cfg,
          out_dim=512,
          idx=0))
      model.add(DenseLayer(
          cfg,
          out_dim=1024,
          idx=1))
      model.add(DenseLayer(
          cfg,
          out_dim=3136,
          act_fn=act_fn_last,
          idx=2))

    elif cfg.DECODER_TYPE == 'conv':
      model.add(Reshape(      # (b, 4, 4, 1)
          (batch_size, 4, 4, -1), name='reshape'))
      model.add(ConvLayer(    # (b, 7, 7, 16)
          cfg,
          kernel_size=3,
          stride=1,
          n_kernel=16,
          resize=7,
          idx=0))
      model.add(ConvLayer(    # (b, 14, 14, 32)
          cfg,
          kernel_size=3,
          stride=1,
          n_kernel=32,
          resize=14,
          idx=1))
      model.add(ConvLayer(    # (b, 28, 28, 16)
          cfg,
          kernel_size=3,
          stride=1,
          n_kernel=16,
          resize=28,
          idx=2))
      model.add(ConvLayer(    # (b, 28, 28, 1)
          cfg,
          kernel_size=3,
          stride=1,
          n_kernel=1,
          act_fn=act_fn_last,
          idx=3))

    elif cfg.DECODER_TYPE == 'conv_t':
      model.add(Reshape(
          (batch_size, 1, 1, -1), name='reshape'))
      model.add(ConvTLayer(
          cfg,
          kernel_size=4,
          stride=1,
          n_kernel=16,
          output_shape=[batch_size, 4, 4, 16],
          padding='VALID',
          act_fn=None,
          idx=0))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn='relu', idx=0))
      model.add(ConvTLayer(
          cfg,
          kernel_size=9,
          stride=1,
          n_kernel=32,
          output_shape=[batch_size, 12, 12, 32],
          padding='VALID',
          act_fn=None,
          idx=1))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn='relu', idx=1))
      model.add(ConvTLayer(
          cfg,
          kernel_size=9,
          stride=1,
          n_kernel=16,
          output_shape=[batch_size, 20, 20, 16],
          padding='VALID',
          act_fn=None,
          idx=2))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn='relu', idx=2))
      model.add(ConvTLayer(
          cfg,
          kernel_size=9,
          stride=1,
          n_kernel=8,
          output_shape=[batch_size, 28, 28, 8],
          padding='VALID',
          act_fn=None,
          idx=3))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn='relu', idx=3))
      model.add(ConvTLayer(
          cfg,
          kernel_size=3,
          stride=1,
          n_kernel=1,
          output_shape=[batch_size, 28, 28, 1],
          act_fn=act_fn_last,
          idx=4))

    else:
      raise ValueError('Wrong decoder type!')

  elif cfg.DATABASE_NAME == 'cifar10':
    if cfg.DECODER_TYPE == 'fc':
      model.add(DenseLayer(
          cfg,
          out_dim=2048,
          idx=0))
      model.add(DenseLayer(
          cfg,
          out_dim=4096,
          idx=1))
      model.add(DenseLayer(
          cfg,
          out_dim=3072,
          act_fn=act_fn_last,
          idx=2))

    elif cfg.DECODER_TYPE == 'conv':
      model.add(Reshape(      # (b, 4, 4, 1)
          (batch_size, 4, 4, -1), name='reshape'))
      model.add(ConvLayer(    # (b, 8, 8, 16)
          cfg,
          kernel_size=3,
          stride=1,
          n_kernel=16,
          idx=0))
      model.add(ConvLayer(    # (b, 16, 16, 32)
          cfg,
          kernel_size=3,
          stride=1,
          n_kernel=32,
          resize=16,
          idx=1))
      model.add(ConvLayer(    # (b, 32, 32, 16)
          cfg,
          kernel_size=3,
          stride=1,
          n_kernel=16,
          resize=32,
          idx=2))
      model.add(ConvLayer(    # (b, 32, 32, 3)
          cfg,
          kernel_size=3,
          stride=1,
          n_kernel=3,
          act_fn=act_fn_last,
          idx=3))

    elif cfg.DECODER_TYPE == 'conv_t':
      model.add(Reshape(
          (batch_size, 1, 1, -1), name='reshape'))
      model.add(ConvTLayer(
          cfg,
          kernel_size=4,
          stride=1,
          n_kernel=16,
          output_shape=[batch_size, 4, 4, 16],
          padding='VALID',
          act_fn=None,
          idx=0))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn='relu', idx=0))
      model.add(ConvTLayer(
          cfg,
          kernel_size=9,
          stride=1,
          n_kernel=32,
          output_shape=[batch_size, 12, 12, 32],
          padding='VALID',
          act_fn=None,
          idx=1))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn='relu', idx=1))
      model.add(ConvTLayer(
          cfg,
          kernel_size=9,
          stride=1,
          n_kernel=16,
          output_shape=[batch_size, 20, 20, 16],
          padding='VALID',
          act_fn=None,
          idx=2))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn='relu', idx=2))
      model.add(ConvTLayer(
          cfg,
          kernel_size=9,
          stride=1,
          n_kernel=8,
          output_shape=[batch_size, 28, 28, 8],
          padding='VALID',
          act_fn=None,
          idx=3))
      model.add(BatchNorm(
          cfg, is_training, momentum=0.99, act_fn='relu', idx=3))
      model.add(ConvTLayer(
          cfg,
          kernel_size=5,
          stride=1,
          n_kernel=3,
          output_shape=[batch_size, 32, 32, 3],
          padding='VALID',
          act_fn=act_fn_last,
          idx=4))

    else:
      raise ValueError('Wrong decoder type!')

  else:
    raise ValueError('Wrong database name!')

  return model.top_layer, model.info


caps_arch = {
  'classifier': classifier,
  'decoder': decoder
}
