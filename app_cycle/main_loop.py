
import sys
from pathlib import Path
import time
from bot.core_loop import MetinBot
from bot.scheduler.bot_scheduler import BotScheduler
from detectors.yolo.capture_and_detect import CaptureAndDetect

from window.metin.metin_window import MetinWindow
from window.multi_window.multi_window_bot_handler import MultiWindowBotHandler
from window.window import windows_swap_fix


FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # versatileMetinBot root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

import cv2 as cv
import utils

class MainLoop():
    def __init__(self):

        self.window_names = ["Ervelia", "Ervelia", "Ervelia", "Ervelia", "Ervelia", "Ervelia"]
        #self.window_names = ["Ervelia"]
        self.change_window = True

        self.handler = MultiWindowBotHandler(self)

        for window_name in self.window_names:
            self.handler.add_instance(window_name)
        self.scheduler = BotScheduler()
        for _, instance in self.handler.instances.items():
            self.scheduler.add_bot(instance['bot'])
        # add initialization after tkinter ui START with tkinter options

        self.capt_detect = self.handler.get_capture_and_detect()
       
        self.last_switch_time = time.time()
        self.switch_interval = 8  # seconds
         
        self.seconds_between_same_runs = 14
        # self.bot = MetinBot(self.metin_window)

    def swap_window(self):
        time.sleep(0.4)
        self.change_window = True
        self.last_switch_time = time.time()

    def start_loop(self):
        
        self.capt_detect.start()

        current_instance = self.handler.get_next_instance()

        pause = False

        while True:
            key = cv.waitKey(1)
            
            if not pause:
            # Check if it's time to switch to the next instance
                current_time = time.time()
                #current_time - self.last_switch_time >= self.switch_interval or
                if self.change_window:
                    self.change_window = False
                    # Stop current bot and capture // update dont stop as it is always stopped
                    #current_instance['bot'].stop(swap_window=False)
                    #print("time of stopped thread {}".format(time.time()))
                    # Move to next instance
                    time.sleep(0.01)
                    #if time.time() - self.handler.get_next_instance_last_run_time() > self.seconds_between_same_runs:
                    #print("window is being changed")
                    new_instance = self.handler.get_next_instance()

                    if new_instance is not None:
                        windows_swap_fix()
                        time.sleep(0.1)
                        try:
                            new_instance['window'].set_window_foreground()
                            time.sleep(0.2)

                            self.capt_detect.change_window_of_detection(new_instance['window'])

                            # current_instance['window'].move_window(0,0)
                            #current_instance['window'].activate()
                            time.sleep(0.1)
                            #change the window in the capt_detect 
                            new_instance['bot'].start()
                            current_instance = new_instance
                            #print("time of started thread {}".format(time.time()))
                            self.handler.set_current_instance_last_run_time()

                            self.last_switch_time = time.time()
                        except Exception as e:
                            print(e)
                            self.change_window = True
                    else:
                        time.sleep(0.2)
                        self.change_window = True

                state_of_detection = current_instance['bot'].get_object_detector_state()

                self.capt_detect.set_object_detector_state(state_of_detection)
                # Get new detections
                screenshot, screenshot_time, detection, detection_time, detection_image = self.capt_detect.get_info()

                # Update bot with new image
                current_instance['bot'].detection_info_update(screenshot, screenshot_time, detection, detection_time)

                if detection_image is None:
                    continue

                # Draw bot state on image
                overlay_image = current_instance['bot'].get_overlay_image() 
                detection_image = cv.addWeighted(detection_image, 1, overlay_image, 1, 0)
 
                # Display image
                cv.imshow('Matches', detection_image)

                # press 'q' with the output window focused to exit.
                # waits 1 ms every loop to process key presses
                if key == ord('w') and not pause: ## w as wait
                    self.capt_detect.stop()
                    current_instance['bot'].stop()
                    pause = True

            if pause:
                key = cv.waitKey(5)
                if key == ord('w'):
                    self.capt_detect.start()
                    current_instance['bot']
                    pause = False

            if key == ord('q'):
                self.capt_detect.stop()
                for window_name in self.window_names:
                    current_instance = self.handler.get_next_instance()
                    current_instance['bot'].stop()
                cv.destroyAllWindows()
                break
