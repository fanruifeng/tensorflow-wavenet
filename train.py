#-*- coding:utf-8 -*-

from __future__ import print_function
from utils import SpeechLoader
from model import Model
import tensorflow as tf #1.12.0
import time
import os

def train():
    # setting parameters
    batch_size = 2
    n_epoch = 100
    n_mfcc = 60

    # load speech data
    wav_path = os.path.join(os.getcwd(), 'data', 'wav', 'train')
    label_file = os.path.join(os.getcwd(), 'data', 'doc', 'trans', 'train.word.txt')
    speech_loader = SpeechLoader(wav_path, label_file, batch_size, n_mfcc)
    n_out = speech_loader.vocab_size

    # load model
    model = Model(n_out, batch_size=batch_size, n_mfcc=n_mfcc)

    tf.summary.scalar('loss', model.cost)
    merged = tf.summary.merge_all()

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        saver = tf.train.Saver(tf.global_variables())
        if len(os.listdir('./model')) > 3:
            print("loading model from checkpoint")
            checkpoint = tf.train.latest_checkpoint('./model')
            saver.restore(sess, checkpoint)

        tf.train.write_graph(sess.graph_def, './model', 'model.pbtxt')
        summary_writer = tf.summary.FileWriter('./model', graph=sess.graph)

        for epoch in range(n_epoch):
            speech_loader.create_batches() # random shuffle data
            speech_loader.reset_batch_pointer()
            for batch in range(speech_loader.n_batches):
                start = time.time()
                batches_wav, batches_label = speech_loader.next_batch()
                feed = {model.input_data: batches_wav, model.targets: batches_label}
                result, train_loss, _ = sess.run([merged, model.cost, model.optimizer_op], feed_dict=feed)
                end = time.time()
                print("epoch: %d/%d, batch: %d/%d, loss: %s, time: %.3f." % (epoch, n_epoch, batch, speech_loader.n_batches,
                                                                             train_loss, end-start))
                summary_writer.add_summary(result, epoch)

            # save models
            if epoch % 5 == 0:
                saver.save(sess, os.path.join(os.getcwd(), 'model','speech.module'), global_step=epoch)


if __name__ == '__main__':
    train()