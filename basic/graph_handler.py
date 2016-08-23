import json
from json import encoder
import os

import tensorflow as tf

from basic.evaluator import Evaluation
from my.utils import short_floats


class GraphHandler(object):
    def __init__(self, config):
        self.config = config
        self.saver = tf.train.Saver()
        self.writer = None
        self.save_path = os.path.join(config.save_dir, config.model_name)

    def initialize(self, sess):
        if self.config.load:
            self._load(sess)
        else:
            sess.run(tf.initialize_all_variables())

        if self.config.mode == 'train':
            self.writer = tf.train.SummaryWriter(self.config.log_dir, graph=tf.get_default_graph())

    def save(self, sess, global_step=None):
        self.saver.save(sess, self.save_path, global_step=global_step)

    def _load(self, sess):
        config = self.config
        if config.load_step > 0:
            save_path = os.path.join(config.save_dir, "{}-{}".format(config.model_name, config.load_step))
        else:
            save_dir = config.save_dir
            checkpoint = tf.train.get_checkpoint_state(save_dir)
            assert checkpoint is not None, "cannot load checkpoint at {}".format(save_dir)
            save_path = checkpoint.model_checkpoint_path
        self.saver.restore(sess, save_path)

    def add_summary(self, summary, global_step):
        self.writer.add_summary(summary, global_step)

    def add_summaries(self, summaries, global_step):
        for summary in summaries:
            self.add_summary(summary, global_step)

    def dump_eval(self, e, precision=2):
        assert isinstance(e, Evaluation)
        path = os.path.join(self.config.eval_dir, "{}-{}.json".format(e.data_type, str(e.global_step).zfill(6)))
        with open(path, 'w') as fh:
            json.dump(short_floats(e.dict, precision), fh)

