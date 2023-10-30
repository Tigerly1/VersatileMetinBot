from threading import Lock
from bot.core_loop import MetinBot
from detectors.yolo.capture_and_detect import CaptureAndDetect

from window.metin.metin_window import MetinWindow


class MultiWindowBotHandler:
    def __init__(self, capture_and_detect, max_instances=6, ):
        self.capture_and_detect = capture_and_detect
        self.instances = {}
        self.lock = Lock()
        self.max_instances = max_instances

    def add_instance(self, window_name):
        with self.lock:
            if len(self.instances) < self.max_instances:
                metin_window = MetinWindow(window_name)
                instance = {
                    'window': metin_window,
                    'capt_detect': self.capture_and_detect,
                    'bot': MetinBot(metin_window)
                }
                self.instances[window_name] = instance

    def get_instance(self, window_name):
        with self.lock:
            return self.instances.get(window_name, None)

    def get_next_instance(self):
        names = list(self.instances.keys())
        if not names:
            return None
        if not hasattr(self, 'current_window_name') or self.current_window_name is None:
            self.current_window_name = names[0]
        else:
            current_index = names.index(self.current_window_name)
            next_index = (current_index + 1) % len(names)
            self.current_window_name = names[next_index]
        return self.instances[self.current_window_name]