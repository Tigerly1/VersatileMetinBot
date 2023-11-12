from threading import Lock
import time
from bot.core_loop import MetinBot
from detectors.yolo.capture_and_detect import CaptureAndDetect

from window.metin.metin_window import MetinWindow

class MultiWindowBotHandler:
    def __init__(self, main_loop, max_instances=8):

        self.instances = {}
        self.lock = Lock()
        self.max_instances = max_instances
        self.counter = 0  # Added counter for unique key generation
        self.main_loop = main_loop

    def add_instance(self, window_name):
        with self.lock:
            if len(self.instances) < self.max_instances:
                metin_window = MetinWindow(window_name)
                if not hasattr(self, 'capture_and_detect') or self.capture_and_detect is None:
                    self.capture_and_detect = CaptureAndDetect(metin_window, r'C:\Users\Filip\Desktop\tob2tm\Metin2-Bot-main\metin_farm_bot\ml\data\yolo\best.pt', None)

                instance = {
                    'window': metin_window,
                    'capt_detect': self.capture_and_detect,
                    'bot': MetinBot(metin_window, self.counter, self.main_loop),
                    'window_name': window_name,  # Store window_name within the instance
                    'last_run_time': time.time()
                }

                ### add time for next move to windows to increase dangeon speed
                if len(self.instances) > 3:
                    instance['bot'].time_of_next_action = time.time() + 240
                elif len(self.instances) > 1:
                    instance['bot'].time_of_next_action = time.time() + 120

                self.instances[self.counter] = instance  # Use counter as the key
                self.counter += 1  # Increment counter for the next instance
                
    def get_capture_and_detect(self):
        return self.capture_and_detect

    def get_instance(self, key):
        with self.lock:
            return self.instances.get(key, None)

    def get_next_instance(self, with_setting_key = True):
        keys = list(self.instances.keys())
        if not keys:
            return None
        if not hasattr(self, 'current_key') or self.current_key is None:
            self.current_key = keys[0]
        else:
            current_index = keys.index(self.current_key)
                # Find the next instance that is ready based on wait_time
            for offset in range(1, len(keys) + 1):
                next_index = (current_index + offset) % len(keys)
                next_key = keys[next_index]
                next_instance = self.instances[next_key]
                elapsed_time = time.time() - next_instance['bot'].time_of_next_action
                if elapsed_time >= 0:  # Use the wait time of the bot
                    if with_setting_key:
                        self.current_key = next_key
                    return next_instance
            return None
        return self.instances[self.current_key]
    
    def set_current_instance_last_run_time(self):
        self.instances[self.current_key]["last_run_time"] = time.time()

    def get_current_instance_last_run_time(self):
        return self.instances[self.current_key]["last_run_time"]
    
    # def set_next_instance_last_run_time(self):
    #     self.get_next_instance(False)
    #     self.instances[self.current_key]["last_run_time"] = time.time()

    def get_next_instance_last_run_time(self):
        next_instance = self.get_next_instance(False)
        return next_instance["last_run_time"]
    
    
