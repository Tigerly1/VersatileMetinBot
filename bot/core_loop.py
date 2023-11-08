from email import utils
import math
import random
import pyautogui
import time
import cv2 as cv
import numpy as np
import enum
from threading import Thread, Lock
import datetime
from bot.ervelia.dangeons.dangeon30_55.state import DangeonState
from bot.ervelia.dangeons.dangeon30_55.state_actions.actions import Actions
from bot.ervelia.game_actions.game_actions import GameActions
from bot.stats.dangeon import DungeonBotStatistics
from utils import * #get_metin_needle_path, get_tesseract_path
import pytesseract
import re
from utils.helpers.paths import get_dangeon_end_image, get_ervelia_metin_needle, get_second_area_dangeon30, get_tesseract_path
import copy

from utils.helpers.vision import MobInfoFilter, Vision
from window.metin.input.interception_input import InterceptionInput
from window.metin.metin_window import MetinWindow
#from credentials import bot_token, chat_id
#import telegram

import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    

class MetinBot:

    def __init__(self, metin_window: MetinWindow, bot_id, main_loop):
        self.metin_window = metin_window
        self.bot_id = bot_id
        self.main_loop = main_loop
        print(metin_window.hwnd)
        self.osk_window = InterceptionInput("Ervelia", metin_window.hwnd)
        #metin_window.move_window(0,0)
        self.vision = Vision()
        self.mob_info_hsv_filter = MobInfoFilter()

        self.screenshot = None
        self.screenshot_time = None
        self.detection_result = None
        self.detection_time = None

        self.overlay_image = None
        self.info_text = ''
        self.delay = None
        self.detected_zero_percent = 0
        self.move_fail_count = 0

        self.calibrate_count = 0
        self.calibrate_threshold = 0
        self.rotate_count = 0
        self.rotate_threshold = 14

        self.started_hitting_time = None
        self.started_moving_time = None
        self.next_metin = None
        self.last_metin_time = time.time()

        self.stopped = False
        self.state_lock = Lock()
        self.info_lock = Lock()
        self.overlay_lock = Lock()

        self.started = time.time()
        self.last_metin_tiome = time.time()
        #@self.send_telegram_message('Started')
        self.metin_count = 0
        self.last_error = None
        self.dangeons_count = 0

        self.current_click = 0
        self.multiple_detection_result = []

        self.current_channel = (int(bot_id) + 2) % 8 + 1
        self.current_metin_respawn = 1
        self.metin_teleports_passed = 0
        self.current_channel_skips = 0

        self.is_object_detector_enabled = True


        self.buff_interval = 76
        self.default_killing_mobs_time = 52
        self.killing_mobs_time = 0
        self.last_buff = time.time()

        self.dangeon_entered_time = time.time()
        self.dangeon_end_time = time.time()

        self.game_actions = GameActions(self)
        self.dangeon_actions = Actions(self)
        self.stats = DungeonBotStatistics()


        pytesseract.pytesseract.tesseract_cmd = get_tesseract_path()

        self.time_of_new_screen = None
        self.time_entered_state = time.time()
        self.health_checks_iterations = 0
        self.state = None
        
        self.login_state = False
        self.login_time = None

        self.time_of_next_action = time.time()

        self.switch_state(DangeonState.INITIALIZING)

        


    def run(self):
        time.sleep(0.13)
        while not self.stopped:
            self.health_checks_iterations = (self.health_checks_iterations + 1) % 7

            if self.health_checks_iterations == 1 \
                and self.state != DangeonState.FIRST_ARENA \
                and self.state != DangeonState.SECOND_ARENA \
                    and self.state != DangeonState.ENTER_THE_DANGEON:
                self.game_actions.health_checks()
            if self.state == DangeonState.INITIALIZING:
                time.sleep(0.3)
                self.metin_window.activate()
                self.game_actions.calibrate_view("guard")
                self.switch_state(DangeonState.ENTER_THE_DANGEON)
                continue

            if self.state == DangeonState.DEBUG:
                # print("XD")
                # text = self.game_actions.get_text_from_current_cursor_position()
                # print(text)
                # time.sleep(0.5)
                continue
                
            if self.state == DangeonState.LOGGING:
                self.game_actions.check_if_player_is_logged_out()
                time.sleep(0.1)
                continue

            if self.state == DangeonState.ENTER_THE_DANGEON:
                self.dangeon_actions.enter_the_dangeon()
                continue

            if self.state == DangeonState.FIRST_ARENA:
                self.dangeon_actions.first_arena()
                continue

            if self.state == DangeonState.KILL_MOBS:
                self.dangeon_actions.kill_mobs()
                continue

            if self.state == DangeonState.KILL_METINS:
                self.dangeon_actions.kill_metins()
                continue

            if self.state == DangeonState.KILL_MINI_BOSS:
                self.dangeon_actions.kill_mini_boss()
                continue

            if self.state == DangeonState.SECOND_ARENA:
                self.dangeon_actions.second_arena()
                continue

            if self.state == DangeonState.GATHER_ITEMS:
                self.dangeon_actions.gather_items()
                continue

            if self.state == DangeonState.SECOND_METINS:
                self.dangeon_actions.second_metins()
                continue

            if self.state == DangeonState.SECOND_MINI_BOSS:
                self.dangeon_actions.second_mini_boss()
                continue
            
            if self.state == DangeonState.END_BOSS:
                self.dangeon_actions.end_boss()
                continue
    
    def brief_detection(self, label):
        time.sleep(0.001)
        try:
            if self.screenshot is not None and self.detection_time is not None:
                if self.detection_result is None or (self.detection_result is not None and self.detection_result['labels'][0] != label):
                    return False
                else:
                    return True
                  
            return False
        except Exception as e:
            print("XD")
            print(e)
            return False
           
    def detect_and_click(self, label, check_match=False, rotate_before_click=False, small_rotation=False):
        try:
            time.sleep(0.01)
            if self.screenshot is not None and self.detection_time is not None and \
                            self.detection_time > self.time_of_new_screen + 0.02:
                #If no matches were found
                if self.detection_result is None or (self.detection_result is not None and self.detection_result['labels'][0] != label):
                    self.put_info_text('No metin found, will rotate!')
                    if self.rotate_count > self.rotate_threshold:
                        self.put_info_text(f'Rotated {self.rotate_count} times -> Recalibrate!')
                        self.calibrate_count += 1
                        self.rotate_count = 0
                        self.game_actions.calibrate_view("guard")
                        self.time_of_new_screen = time.time()
                        self.stop()
                    else:
                        self.rotate_count += 1
                        self.game_actions.rotate_view(small_rotation)
                        self.time_of_new_screen = time.time()
                    return False
                else:
                    saved_click_pos = copy.deepcopy(self.detection_result['click_pos'])
                    self.rotate_count = 0
                    if rotate_before_click:
                        self.game_actions.rotate_using_space_before_click()
                    if label == "first_arena":
                        x, y = saved_click_pos
                        y = y + 75
                        x = x - 30 
                        self.metin_window.mouse_move(x,y)
                    
                    else:
                    # self.put_info_text(f'Best match width: {self.detection_result["best_rectangle"][2]}')
                        self.metin_window.mouse_move(*saved_click_pos)
                    
                    if label == "second_arena":
                        self.osk_window.activate_flag()

                    time.sleep(0.03)
                    if not check_match:
                        self.metin_window.mouse_click()
                        time.sleep(0.02)
                        return True
                    else:
                        is_correct = self.check_match_after_detection(label)
                        return is_correct
            return False
        except Exception as e:
            print(e)
            return False
            
    def check_match_after_detection(self, label):
        detection_success = False
        match_loc = None
        if label=="guard":
            time.sleep(0.03)
            text = self.game_actions.get_text_from_current_cursor_position()
            if "Stra" in text or "Myr" in text or "Dol" in text:
                detection_success = True
        else:
            time.sleep(0.07)
            pos = self.metin_window.get_relative_mouse_pos()
            width = 200
            height = 150
            top_left = self.metin_window.limit_coordinate((int(pos[0] - width / 2), pos[1] - height))
            bottom_right = self.metin_window.limit_coordinate((int(pos[0] + width / 2), pos[1]))
            try:
                self.info_lock.acquire()
                logging.debug("Lock acquired for check_match_after_detection.")
                time.sleep(0.02)
                new_screen_after_hovering = self.metin_window.capture()
                time.sleep(0.02)

                if len(new_screen_after_hovering) > 0:
                    mob_title_box = self.vision.extract_section(new_screen_after_hovering, top_left, bottom_right)
                    
                    logging.debug("Template matching for label.")
                    match_loc, match_val = self.vision.template_match_alpha(mob_title_box, get_ervelia_metin_needle(), 2000000)
            except Exception as e:
                logging.error("Exception occurred in check_match_after_detection: %s", e, exc_info=True)
            finally:
                self.info_lock.release()
                logging.debug("Lock released after check_match_after_detection.")

        if match_loc is not None or detection_success:
            self.metin_window.mouse_click()
            time.sleep(0.02)
            #self.osk_window.activate_dodge(self.current_metin_name=="water")
            #self.osk_window.activate_horse_dodge()
            time.sleep(0.02)
            #self.set_object_detector_state(False)
            self.put_info_text('{} found!'.format(label))
            #self.game_actions.turn_on_buffs()
            is_moving_to_enemy = True
            # while is_moving_to_enemy:
            #     is_moving_to_enemy = self.moving_to_enemy()
            #     if not is_moving_to_enemy:
            #         return True
            # time.sleep(7.5)
            return True
            #self.osk_window.ride_through_units()
            #self.switch_state(BotState.MOVING)

        else:
            
            try:
                self.put_info_text('No metin found -> rotate and search again!')
                self.game_actions.rotate_view()
                self.rotate_count += 1
                return False

            except Exception as e:

                self.put_info_text('No metin found -> rotate and search again!')
                self.game_actions.rotate_view()
                self.rotate_count += 1
                return False            



    def moving_to_enemy(self):
        if self.started_moving_time is None:
            self.started_moving_time = time.time()

        result = self.game_actions.get_mob_info()
        #print(result[0])
        if result is not None and result[1] < 1000:
            self.started_moving_time = None
            self.move_fail_count = 0
            self.put_info_text(f'Started hitting {result[0]}')
            is_hitting_enemy = True
            while is_hitting_enemy:
                is_hitting_enemy = self.hitting_enemy()
                if not is_hitting_enemy:
                    return False
            

        elif time.time() - self.started_moving_time >= 9:
            self.started_moving_time = None
            return None
            #self.osk_window.pick_up()
            #self.metin_count += 1
        return True
    
    def hitting_enemy(self):
        self.rotate_count = 0
        self.calibrate_count = 0
        self.move_fail_count = 0

        if self.started_hitting_time is None:
            self.started_hitting_time = time.time()

        self.game_actions.respawn_if_dead()
        result = self.game_actions.get_mob_info()
        #print(result)
        if result is None or time.time() - self.started_hitting_time >= 9:
            self.started_hitting_time = None
            self.put_info_text('Finished -> Collect drop')
            self.metin_count += 1
            total = int(time.time() - self.started)
            # if int(self.last_metin_time) + 90 < total:
            #     self.game_actions.calibrate_view()
            self.last_metin_time = total

            return False
        return True

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()
        
    def set_object_detector_state(self,state):
        self.state_lock.acquire()
        self.is_object_detector_enabled = state
        self.state_lock.release()


    def get_object_detector_state(self):
        self.state_lock.acquire()
        state = self.is_object_detector_enabled
        self.state_lock.release()
        return state

    def stop(self, swap_window=True, time_of_next_action=time.time()):
        self.state_lock.acquire()
        self.time_of_next_action = time_of_next_action
        self.stopped = True
        if swap_window:
            self.main_loop.swap_window()
        self.state_lock.release()


    def close_window_if_not_working(self):
        total = int(time.time() - self.started)
        if total - int(self.last_metin_time) > 600:
            self.metin_window.find_process_and_kill_window()
            self.last_metin_time = total

    def detection_info_update(self, screenshot, screenshot_time, result, result_time):
        self.info_lock.acquire()
        self.screenshot = screenshot
        self.screenshot_time = screenshot_time
        self.detection_result = result
        self.detection_time = result_time
        self.info_lock.release()

    def get_screenshot_info(self):
        self.info_lock.acquire()
        screenshot = self.screenshot
        self.info_lock.release()
        return screenshot

    def switch_state(self, state):
        self.stop()
        self.state_lock.acquire()
        self.stats.add_state_time(self.state.name, time.time() - self.time_entered_state )
        self.state = state
        self.time_of_new_screen = time.time()
        self.time_entered_state = time.time()
        self.state_lock.release()
        self.put_info_text()
       

    def increment_state(self, stop_thread=True, time_of_next_acion=time.time()):
        
        self.state_lock.acquire()
        self.stats.add_state_time(self.state.name, time.time() - self.time_entered_state )
        if self.state != DangeonState.DEBUG and self.state != DangeonState.END_BOSS:
            self.state = DangeonState(self.state.value + 1)
        elif self.state == DangeonState.END_BOSS:
            self.state = DangeonState(0)
        self.time_entered_state = time.time()
        self.time_of_next_action = time_of_next_acion
        self.state_lock.release()
        self.put_info_text()
        if stop_thread:
            self.stop()
        

    def get_state(self):
        self.state_lock.acquire()
        state = self.state
        self.state_lock.release()
        return state

    def put_info_text(self, string=''):
        if len(string) > 0:
            self.info_text += datetime.datetime.now().strftime("%H:%M:%S") + ': ' + string + '\n'
        font, scale, thickness = cv.FONT_HERSHEY_SIMPLEX, 0.35, 1
        lines = self.info_text.split('\n')
        text_size, _ = cv.getTextSize(lines[0], font, scale, thickness)
        y0 = 720 - len(lines) * (text_size[1] + 6)

        self.overlay_lock.acquire()
        self.overlay_image = np.zeros((self.metin_window.height, self.metin_window.width, 3), np.uint8)
        self.put_text_multiline(self.overlay_image, self.state.name, 10, 715, scale=0.5, color=(0, 255, 0))
        self.put_text_multiline(self.overlay_image, self.info_text, 10, y0, scale=scale)
        self.overlay_lock.release()

    def get_overlay_image(self):
        self.overlay_lock.acquire()
        overlay_image = self.overlay_image.copy()
        self.overlay_lock.release()
        return overlay_image

    def put_text_multiline(self, image, text, x, y, scale=0.3, color=(0, 200, 0), thickness=1):
        font = font = cv.FONT_HERSHEY_SIMPLEX
        y0 = y
        for i, line in enumerate(text.split('\n')):
            text_size, _ = cv.getTextSize(line, font, scale, thickness)
            line_height = text_size[1] + 6
            y = y0 + i * line_height
            if y > 300:
                cv.putText(image, line, (x, y), font, scale, color, thickness)

   
    


