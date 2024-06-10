import logging
import threading
import queue

class LogCapturer:
    def __init__(self):
        self.log_queue = queue.Queue()
        self.log_handler = logging.StreamHandler(self)
        self.log_handler.setLevel(logging.INFO)
        self.log_formatter = logging.Formatter('%(message)s')
        self.log_handler.setFormatter(self.log_formatter)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.log_handler)
    
    def write(self, message):
        if message.strip() != "":  # Ignore empty messages
            self.log_queue.put(message)
    
    def flush(self):
        pass
    
    def start_logging(self):
        self.log_thread = threading.Thread(target=self._log_thread)
        self.log_thread.start()
    
    def _log_thread(self):
        while True:
            message = self.log_queue.get()
            print(message)
            self.log_queue.task_done()
    
    def get_log_contents(self):
        log_contents = []
        while not self.log_queue.empty():
            log_contents.append(self.log_queue.get())
            self.log_queue.task_done()
        return log_contents

log_capturer = LogCapturer()
log_capturer.start_logging()
