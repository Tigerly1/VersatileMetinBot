
import datetime
import sys
from pathlib import Path
import threading
import time
from bot.core_loop import MetinBot
from detectors.yolo.capture_and_detect import CaptureAndDetect
from utils.helpers.vision import Vision

from window.metin.metin_window import MetinWindow
from window.multi_window.multi_window_bot_handler import MultiWindowBotHandler
from window.window import windows_swap_fix

import utils.interception as interceptionModule
from utils.interception import Interception
from utils.interception import Stroke
interceptionModule.inputs.keyboard = 0
interceptionModule.inputs.mouse = 10
from utils.interception._keycodes import KEYBOARD_MAPPING
from utils.interception._consts import *


FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # versatileMetinBot root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

import cv2 as cv
import utils

class MainLoop():
    def __init__(self):

        self.windows_count = 6
        self.server_name = "Ervelia"
        
        self.window_names = []
        for x in range(0, self.windows_count):
            self.window_names.append(self.server_name)

        #self.window_names = ["Ervelia", "Ervelia", "Ervelia", "Ervelia", "Ervelia", "Ervelia"]
        #self.window_names = ["Ervelia", "Ervelia"]
        
        self.change_window = False

        self.handler = MultiWindowBotHandler(self)

        for window_name in self.window_names:
            self.handler.add_instance(window_name)
        
        self.capt_detect = self.handler.get_capture_and_detect()
        #self.time_to_stop_for_scalene = time.time()
        self.last_switch_time = time.time()
        self.switch_interval = 8  # seconds
         
        self.seconds_between_same_runs = 14
        # self.bot = MetinBot(self.metin_window)
        self.stop_loop = False
        interception = Interception()
        keyboard_thread = threading.Thread(target=self.listen_for_ctrl_w, args=(interception,))
        keyboard_thread.start()

    def swap_window(self):
        time.sleep(0.02)
        self.change_window = True
        self.last_switch_time = time.time()

    def start_loop(self):
        
        self.capt_detect.start()

        current_instance = self.handler.get_next_instance()
        windows_swap_fix()
        current_instance['window'].set_window_foreground()
        self.capt_detect.change_window_of_detection(current_instance['window'])

        while True:
            screenshot, screenshot_time, detection, detection_time, detection_image, hwnd_of_ss = self.capt_detect.get_info()

            if hwnd_of_ss == current_instance['bot'].metin_window.hwnd:
                time.sleep(0.002)
                screenshot, screenshot_time, detection, detection_time, detection_image, hwnd_of_ss = self.capt_detect.get_info()
                current_instance['bot'].detection_info_update(screenshot, screenshot_time, detection, detection_time)
                break
            # Update bot with new image
        # if detection_image is None:
        #     self.swap_window()
        
        current_instance['bot'].start()
        self.handler.set_current_instance_last_run_time()

        while True:
            key = cv.waitKey(1)
            # if time.time() - 90 >= self.time_to_stop_for_scalene:
            #                 scalene_profiler.stop()
            if not self.stop_loop:
            # Check if it's time to switch to the next instance
                current_time = time.time()
                #current_time - self.last_switch_time >= self.switch_interval or
                if self.change_window:
                    
                    #print("time before stopped thread {}".format(time.time()))
                    #print("time of start changing window {}".format(time.time()))
                    current_instance['bot'].wait_for_thread_to_terminate()
                    self.change_window = False
                    # Move to next instance
                    ##time.sleep(0.01)
                    #if time.time() - self.handler.get_next_instance_last_run_time() > self.seconds_between_same_runs:
                    #print("window is being changed")
                    new_instance = self.handler.get_next_instance()
                    ##time.sleep(0.01)
                    if new_instance is not None and ((current_instance['bot'].thread is not None and not current_instance['bot'].thread.is_alive()) \
                                                     or current_instance['bot'].thread is None):
                        
                        try:
                            if new_instance != current_instance:

                                windows_swap_fix()

                                new_instance['window'].set_window_foreground()
                                #time.sleep(0.03)

                                self.capt_detect.change_window_of_detection(new_instance['window'])

                                if new_instance['bot'].does_it_need_newest_window_detections_after_swap:
                                    while new_instance['bot'].does_it_need_newest_window_detections_after_swap:
                                        screenshot, screenshot_time, detection, detection_time, detection_image, hwnd_of_ss = self.capt_detect.get_info()
                            
                                        if hwnd_of_ss == new_instance['bot'].metin_window.hwnd:
                                            time.sleep(0.002)
                                            new_instance['bot'].detection_info_update(screenshot, screenshot_time, detection, detection_time)
                                            break
                                        # Update bot with new image
                                    

                                else:
                                    screenshot, screenshot_time, detection, detection_time, detection_image, hwnd_of_ss = self.capt_detect.get_info()
                                    new_instance['bot'].detection_info_update(screenshot, screenshot_time, detection, detection_time)

                                if detection_image is None:
                                        self.swap_window()
                                        continue
                                # Draw bot state on image
                                overlay_image = current_instance['bot'].get_overlay_image() 
                                detection_image = cv.addWeighted(detection_image, 1, overlay_image, 1, 0)
                    
                                #Vision().SIFT_FEATURES_DETECTION(detection_image)
                                # Display image
                                cv.imshow('Matches', detection_image)

                            new_instance['window'].set_window_foreground()
                            time.sleep(0.03)
                            new_instance['bot'].start()
                            current_instance = new_instance
                            #print("time of started thread {}".format(time.time()))
                            self.handler.set_current_instance_last_run_time()

                            self.last_switch_time = time.time()
                            #print("time on end of changing window {}".format(time.time()))
                        except Exception as e:
                            #print(e)
                            self.swap_window()
                    else:
                        self.swap_window()

                state_of_detection = current_instance['bot'].get_object_detector_state()

                self.capt_detect.set_object_detector_state(state_of_detection)

                # Get new detections
                screenshot, screenshot_time, detection, detection_time, detection_image, hwnd_of_ss = self.capt_detect.get_info()
                
                if hwnd_of_ss == current_instance['bot'].metin_window.hwnd:
                # Update bot with new image
                    current_instance['bot'].detection_info_update(screenshot, screenshot_time, detection, detection_time)

                if detection_image is None:
                    continue

                overlay_image = current_instance['bot'].get_overlay_image() 
                detection_image = cv.addWeighted(detection_image, 1, overlay_image, 1, 0)

                cv.imshow('Matches', detection_image)
                #print("time of iteration {}".format(time.time()))

            if self.stop_loop: ## w as wait
                self.capt_detect.stop()
                current_instance['bot'].stop(swap_window=False)

           
                    

            if key == ord('q'):
                self.capt_detect.stop()
                for window_name in self.window_names:
                    current_instance = self.handler.get_next_instance()
                    current_instance['bot'].stop()
                cv.destroyAllWindows()
                break

    def listen_for_ctrl_w(self, interception):
        while True:
            context = Interception()
            context.set_filter(context.is_keyboard, FilterKeyState.FILTER_KEY_ALL)
            ctrl_clicked = False
            try:
                while True:
                    device = context.wait()
                    stroke = context.receive(device)

                    

                    if stroke.code == KEYBOARD_MAPPING['w'] and ctrl_clicked:
                        self.stop_loop = not self.stop_loop
                        if self.stop_loop:
                            print("bot is stopped now")
                        if not self.stop_loop:
                            self.capt_detect.start()
                            self.swap_window()
                        break

                    if stroke.code in [KEYBOARD_MAPPING['shift'], KEYBOARD_MAPPING['shift']]:
                        ctrl_clicked = True
                    else:
                        ctrl_clicked = False

                    if stroke.code == 0x01:
                        print("ESC pressed, exited.")
                        #return device


                    context.send(device, stroke)
            finally:
                context._destroy_context()
                