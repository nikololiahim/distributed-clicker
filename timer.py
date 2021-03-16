import time
import threading



class OutOfTimeException(BaseException):
    def __init__(self):
        super(OutOfTimeException, self).__init__()


class Timer(threading.Thread):

    def __init__(self, time_left):
        self.OUT_OF_TIME = threading.Event()
        super(Timer, self).__init__()
        self.time_left = time_left
        self.current_time = 0
        assert self.time_left > 0
        self.daemon = True
        self.STOPPED = False
        self.times_done = 0

    def run(self):
        while True:
            self.start = time.perf_counter()
            self.current_time = time.perf_counter() - self.start
            while self.current_time < self.time_left:
                if not self.STOPPED:
                    self.current_time = time.perf_counter() - self.start
                    time.sleep(1)
            self.times_done += 1
            self.OUT_OF_TIME.set()

    def reset(self):
        self.times_done = 0
        self.start = time.perf_counter()
        self.OUT_OF_TIME.clear()

    def stop(self):
        self.STOPPED = True