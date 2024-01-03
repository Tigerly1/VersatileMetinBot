from threading import Lock
import time
from bot.core_loop import MetinBot
from bot.ervelia.dangeons.dangeon30_55.state_order import Dangeon30StateOrder
from bot.ervelia.dangeons.dangeon75_95.state_order import Dangeon75StateOrder
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
                    'bot': MetinBot(metin_window, Dangeon75StateOrder(), self.counter, self.main_loop),
                    'window_name': window_name,  # Store window_name within the instance
                    'last_run_time': time.time()
                }

                ## add time for next move to windows to increase dangeon speed
                # if len(self.instances) > 3:
                #     instance['bot'].time_of_next_action = time.time() + 120
                # elif len(self.instances) > 1:
                #     instance['bot'].time_of_next_action = time.time() + 60

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

        # Start from the current key, or from the beginning if there is no current key
        current_index = keys.index(self.current_key) if hasattr(self, 'current_key') and self.current_key is not None else -1

        highest_priority_instance = None
        highest_priority_value = -1  # Assuming priority is always non-negative

        # Iterate over the instances starting from the current index
        for offset in range(1, len(keys) + 1):
            next_index = (current_index + offset) % len(keys)
            next_key = keys[next_index]
            next_instance = self.instances[next_key]
            elapsed_time = time.time() - next_instance['bot'].time_of_next_action

            if elapsed_time >= 0:  # Instance is ready
                # Get the priority of this instance, default to 0 if not set
                priority = getattr(next_instance['bot'], 'priority', 0)

                # Check if this instance has the highest priority so far
                if priority > highest_priority_value:
                    highest_priority_value = priority
                    highest_priority_instance = (next_key, next_instance)

        # If no ready instance is found, return None
        if highest_priority_instance is None:
            return None

        # If a highest priority instance was found, update the current key and return it
        if with_setting_key:
            self.current_key = highest_priority_instance[0]

        return highest_priority_instance[1]
    
    def set_current_instance_last_run_time(self):
        self.instances[self.current_key]["last_run_time"] = time.time()

    def get_current_instance_last_run_time(self):
        return self.instances[self.current_key]["last_run_time"]
    
    # def set_next_instance_last_run_time(self):
    #     self.get_next_instance(False)
    #     self.instances[self.current_key]["last_run_time"] = time.time()

    # def get_next_instance_last_run_time(self):
    #     next_instance = self.get_next_instance(False)
    #     return next_instance["last_run_time"]
    
    
