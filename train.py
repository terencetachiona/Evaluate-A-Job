#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author:lthan
# @Email :xiaohan809@qq.com
# @Time  :2017/9/7 10:35

import tensorflow as tf
import numpy as np
import os
import time
import datetime
from codes.data_helpers import DataHelper
from codes.text_cnn import TextCNN
from tensorflow.contrib import learn

# Parameters
# ===================================

# Data loading params
tf.flags.DEFINE_float('dev_sample_precentage',0.1,'Percentage of the training data to use for validation.')
tf.flags.DEFINE_string('data_file','../inputs/cv_test','Data source file.')
tf.flags.DEFINE_string('skillwords_file','../inputs/skill_words','the skill words file.')

# Model Hyperparaeters
tf.flags.DEFINE_integer('embedding_dim',128,'Dimensionality of character embedding(default:128)')
tf.flags.DEFINE_string('filter_sizes','3,4,5','Comma-separated filter sizes(default:3,4,5)')
tf.flags.DEFINE_integer('num_filters',128,'number of filters per filter size (default:128)')
tf.flags.DEFINE_float('dropout_keep_prob',0.5,'Dropout keep probability(default:0.5)')
tf.flags.DEFINE_float('l2_reg_lambda',3.0,'L2 regularization lambda(default:0.0)')

# Training parameters
tf.flags.DEFINE_integer('batch_size',64,'Batch size (default:64)')
tf.flags.DEFINE_integer('num_epochs',200,'Number of training epochs(default:200)')
tf.flags.DEFINE_integer('evaluate_every',100,'Evaluate model on dev set after this many stpes(default:100)')
tf.flags.DEFINE_integer('checkpoint_every',100,'Save model after this many steps (default: 100)')
tf.flags.DEFINE_integer('num_checkpoints',5,'Number of checkpoints to stored(default: 5)')

#Misc Parameters
tf.flags.DEFINE_boolean('allow_soft_placement',True,'Allow device soft device placement')
tf.flags.DEFINE_boolean('log_device_placement',False,'Log placement of ops on devices')

FLAGS = tf.flags.FLAGS
FLAGS._parse_flags()
print('\nParameters:')
for attr,val in sorted(FLAGS.__flags.items()):
    print("{}={}".format(attr.upper(),val))
print("")

# Data Preparation
# =============================
print('Loading data...')
dh = DataHelper()
x_text,y_ =dh.load_datasets(FLAGS.data_file,FLAGS.skillwords_file)
# Build vocabulary
max_document_length = max([len(x.split(" ")) for x in x_text])
vocab_processor = learn.preprocessing.VocabularyProcessor(max_document_length)
x = np.array(list(vocab_processor.fit_transform(x_text)))
y_ = np.array(y_)
# Randomly shuffle data
np.random.rand(10)
shuffle_indices = np.random.permutation(np.arange(len(y_)))

x_shuffled = x[shuffle_indices]
y_shuffled = y_[shuffle_indices]

#Split train/test set
# TODO: This is very crude, should use cross-validation
dev_sample_index = -1 * int(FLAGS.dev_sample_precentage * float(len(y_)))
x_train,x_dev = x_shuffled[:dev_sample_index],x_shuffled[dev_sample_index:]
y_train,y_dev = y_shuffled[:dev_sample_index],y_shuffled[dev_sample_index:]

print("Vocabulary Size:{:d}".format(len(vocab_processor.vocabulary_)))
print("Train/Dev split:{:d}/{:d}".format(len(y_train),len(y_dev)))

# Training
# ==========================================

with tf.Graph().as_default():
    session_conf = tf.ConfigProto(
        allow_soft_placement = FLAGS.allow_soft_placement,
        log_device_placement = FLAGS.log_device_placement)
    sess = tf.Session(config=session_conf)
    with sess.as_default():
        cnn = TextCNN(
            sequence_length=x_train.shape[1],
            vocab_size=len(vocab_processor.vocabulary_),
            embedding_size=FLAGS.embedding_dim,
            filter_sizes=list(map(int,FLAGS.filter_sizes.split(','))),
            num_filters=FLAGS.num_filters,
            l2_reg_lambda=FLAGS.l2_reg_lambda
        )

        # Define Training procedure
        global_step = tf.Variable(0,name='global_step',trainable=False)
        optimizer = tf.train.AdamOptimizer(1e-3)
        grads_and_vars = optimizer.compute_gradients(cnn.loss)
        train_op = optimizer.apply_gradients(grads_and_vars,global_step=global_step)

        # Keep track of gradient values and sparsity (optional)
        grad_summaries = []
        for g, v in grads_and_vars:
            if g is not None:
                grad_hist_summary = tf.summary.histogram("{}/grad/hist".format(v.name), g)
                sparsity_summary = tf.summary.scalar("{}/grad/sparsity".format(v.name), tf.nn.zero_fraction(g))
                grad_summaries.append(grad_hist_summary)
                grad_summaries.append(sparsity_summary)
        grad_summaries_merged = tf.summary.merge(grad_summaries)

        # Output directory for models and summaries
        timestamp = str(int(time.time()))
        out_dir = os.path.abspath(os.path.join(os.path.curdir, "../runs", timestamp))
        print("Writing to {}\n".format(out_dir))
        # Summaries for loss
        loss_summary = tf.summary.scalar("loss", cnn.loss)
        # Train Summaries
        train_summary_op = tf.summary.merge([loss_summary, grad_summaries_merged])
        train_summary_dir = os.path.join(out_dir, "summaries", "train")
        train_summary_writer = tf.summary.FileWriter(train_summary_dir, sess.graph)

        # Dev summaries
        dev_summary_op = tf.summary.merge([loss_summary])
        dev_summary_dir = os.path.join(out_dir, "summaries", "dev")
        dev_summary_writer = tf.summary.FileWriter(dev_summary_dir, sess.graph)
        # Checkpoint directory. Tensorflow assumes this directory already exists so we need to create it
        checkpoint_dir = os.path.abspath(os.path.join(out_dir, "checkpoints"))
        checkpoint_prefix = os.path.join(checkpoint_dir, "model")
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)
        saver = tf.train.Saver(tf.global_variables(), max_to_keep=FLAGS.num_checkpoints)

        # Write vocabulary
        vocab_processor.save(os.path.join(out_dir, "vocab"))

        # Initialize all variables
        sess.run(tf.global_variables_initializer())

        def train_step(x_batch,y_batch):
            '''
            A single training step
            :param x_batch:
            :param y_batch:
            :return:
            '''
            feed_dict = {
                cnn.input_x : x_batch,
                cnn.input_y : y_batch,
                cnn.dropout_keep_prob : FLAGS.dropout_keep_prob
            }
            _,step,summaries,loss = sess.run(
                [train_op,global_step,train_summary_op,cnn.loss],
                feed_dict
            )
            time_str = datetime.datetime.now().isoformat()
            print("{}: step {}, loss {:g}".format(time_str, step, loss))
            train_summary_writer.add_summary(summaries, step)

        def dev_step(x_batch,y_batch,writer=None):
            '''
            Evaluates model on a dev set
            :param x_batch:
            :param y_batch:
            :param writer:
            :return:
            '''
            feed_dict = {
                cnn.input_x : x_batch,
                cnn.input_y : y_batch,
                cnn.dropout_keep_prob : 1.0
            }
            step,summaries,loss,predictions = sess.run(
                [global_step,dev_summary_op,cnn.loss,cnn.predictions],
                feed_dict=feed_dict
            )
            for i in range(y_batch.shape[0]):
                print(predictions[i],y_batch[i])
            time_str = datetime.datetime.now().isoformat()
            print("{}:stop {}, loss {:g}".format(time_str,step,loss))
            if writer:
                writer.add_summary(summaries, step)
        # Generate batches
        batches = dh.batch_iter(
            list(zip(x_train,y_train)),FLAGS.batch_size,FLAGS.num_epochs)

        # Training loop . For each batch...
        for batch in batches:
            x_batch,y_batch = zip(*batch)
            train_step(x_batch,y_batch)
            current_step = tf.train.global_step(sess,global_step)
            if current_step % FLAGS.evaluate_every == 0:
                print("\nEvaluation:")
                dev_step(x_dev,y_dev,writer=dev_summary_writer)
                print("")
            if current_step % FLAGS.checkpoint_every == 0:
                path = saver.save(sess, checkpoint_prefix, global_step=current_step)
                print("Saved model checkpoint to {}\n".format(path))
