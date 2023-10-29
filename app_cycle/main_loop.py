
import sys
from pathlib import Path
from bot.core_loop import MetinBot
from detectors.yolo.capture_and_detect import CaptureAndDetect

from window.metin.metin_window import MetinWindow

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # versatileMetinBot root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

import cv2 as cv
import utils

class MainLoop():
    def __init__(self):


        # add initialization after tkinter ui START with tkinter options


        self.metin_window = MetinWindow('Ervelia')
        self.capt_detect = CaptureAndDetect(self.metin_window, r'C:\Users\Filip\Desktop\tob2tm\Metin2-Bot-main\metin_farm_bot\ml\data\yolo\best.pt', None)
        self.bot = MetinBot(self.metin_window)


    def start_loop(self):
        
        self.capt_detect.start()
        
        self.bot.start()

        pause = False

        while True:

            key = cv.waitKey(1)
            if not pause:

                state_of_detection = self.bot.get_object_detector_state()

                self.capt_detect.set_object_detector_state(state_of_detection)
                # Get new detections
                screenshot, screenshot_time, detection, detection_time, detection_image = self.capt_detect.get_info()

                # Update bot with new image
                self.bot.detection_info_update(screenshot, screenshot_time, detection, detection_time)

                if detection_image is None:
                    continue

                # Draw bot state on image
                overlay_image = self.bot.get_overlay_image() 
                detection_image = cv.addWeighted(detection_image, 1, overlay_image, 1, 0)

                # Display image
                cv.imshow('Matches', detection_image)

                # press 'q' with the output window focused to exit.
                # waits 1 ms every loop to process key presses
                if key == ord('w') and not pause: ## w as wait
                    self.capt_detect.stop()
                    self.bot.stop()
                    pause = True

            if pause:
                key = cv.waitKey(5)
                if key == ord('w'):
                    self.capt_detect.start()
                    self.bot.start()
                    pause = False

            if key == ord('q'):
                self.capt_detect.stop()
                self.bot.stop()
                cv.destroyAllWindows()
                break

        print('Done.')