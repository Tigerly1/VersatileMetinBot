
import sys
from pathlib import Path
import time
from bot.core_loop import MetinBot
from bot.scheduler.bot_scheduler import BotScheduler
from detectors.yolo.capture_and_detect import CaptureAndDetect

from window.metin.metin_window import MetinWindow
from window.multi_window.multi_window_bot_handler import MultiWindowBotHandler


FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # versatileMetinBot root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

import cv2 as cv
import utils

class MainLoop():
    def __init__(self):

        window_names = [1,2,3]
        self.capt_detect = CaptureAndDetect(self.metin_window, r'C:\Users\Filip\Desktop\tob2tm\Metin2-Bot-main\metin_farm_bot\ml\data\yolo\best.pt', None)
        self.handler = MultiWindowBotHandler(capture_and_detect=self.capt_detect)
        for window_name in window_names:
            self.handler.add_instance(window_name)
        self.scheduler = BotScheduler()
        for _, instance in self.handler.instances.items():
            self.scheduler.add_bot(instance['bot'])
        # add initialization after tkinter ui START with tkinter options


        self.metin_window = MetinWindow('Ervelia')
        # self.bot = MetinBot(self.metin_window)


    def start_loop(self):
        
        self.capt_detect.start()
        
        # self.bot.start()

        last_switch_time = time.time()
        switch_interval = 2.0  # seconds

        current_instance = self.handler.get_next_instance()

        pause = False

        while True:
            key = cv.waitKey(1)
            
            if not pause:
            # Check if it's time to switch to the next instance
                current_time = time.time()
                if current_time - last_switch_time >= switch_interval:
                    # Stop current bot and capture
                    current_instance['bot'].stop()

                    # Move to next instance
                    current_instance = self.handler.get_next_instance()

                    #change the window in the capt_detect 
                    current_instance['bot'].start()

                    current_instance['window'].set_window_foreground()

                    last_switch_time = current_time

                
                

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
                current_instance['bot'].stop()
                cv.destroyAllWindows()
                break

        print('Done.')