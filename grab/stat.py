import logging
from collections import defaultdict
import time
from contextlib import contextmanager


class Stat(object):
    def __init__(self, logger_name='stat', log_file=None):
        self.time = time.time()
        self.count_prev = 0
        self.counters = defaultdict(int)
        self.collections = defaultdict(list)
        self.time_points = {}
        self.timers = defaultdict(int)
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        if log_file:
            self.logger.addHandler(logging.FileHandler(log_file, 'w'))
            self.logger.setLevel(logging.DEBUG)

    def get_counters_line(self):
        items = []
        for key in sorted(self.counters.keys):
            if key is not None:
                items.append('%s:%d' % (key, self.items_counters[key]))
        return '/'.join(items)

    def inc(self, key=None, delta=1):
        self.counters[key] += delta
        count_current = self.counters[None]
        now = time.time()
        if now - self.time > 5:
            diff = count_current - self.count_prev
            qps = diff / (now - self.time) 
            self.logger.debug(
                'rps: %.2f [%s]' % (qps, self.get_counters_line()))
            self.count_prev = count_current
            self.time = now

    def append(self, key, val):
        self.collections[key].append(val)

    def start_timer(self, key):
        self.time_points[key] = time.time()

    def stop_timer(self, key):
        start = self.time_points[key]
        now = time.time()
        total = now - start
        self.timers[key] += total
        del self.time_points[key]
        return total

    @contextmanager
    def log_time(self, key):
        self.start_timer(key)
        try:
            yield
        finally:
            self.stop_timer(key)