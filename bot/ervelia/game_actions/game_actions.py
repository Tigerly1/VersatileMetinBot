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
import pytesseract
import re
from utils.helpers.music_player import play_music
from utils.helpers.paths import ERVELIA_DANG30_IMAGE_PATHS, get_dangeon_enter_the_dangeon_button, get_dangeon_you_cannot_enter_the_dangeon_button, get_empty_mount_image, get_eq_ervelia_stripe, gm_icon_image
from utils.helpers.tesseract_texts import TEXTS_FOR_ACTION, check_if_text_from_image_includes_the_text
from window.window import windows_swap_fix


class GameActions:
    def __init__(self, metin_bot):
        self.metin_bot = metin_bot
        self.calibration_step = 0

    def zoom_out(self, zooming_time=1.0, accurate=True):
        self.metin_bot.osk_window.start_zooming_out()
        if accurate:
            time.sleep(zooming_time)
        else:
            time.sleep(0.05)
            windows_swap_fix(True)
        #time.sleep(zooming_time)
        self.metin_bot.osk_window.stop_zooming_out()

    def zoom_in(self, zooming_time=1.0, accurate=True):
        self.metin_bot.osk_window.start_zooming_in()
        if accurate:
            time.sleep(zooming_time)
        else:
            time.sleep(0.05)
            windows_swap_fix(True)
            
        #time.sleep(zooming_time)
        self.metin_bot.osk_window.stop_zooming_in()

    def zoom_in_out(self, in_time=1.0, out_time=0.6):
        if self.calibration_step == 0:
            self.zoom_in(in_time, False)
            self.calibration_step = 1
            time.sleep(0.05)
            self.metin_bot.stop(True, time.time()+1.3, 0, False)
            return
        elif self.calibration_step == 1:
            self.zoom_out(out_time)
            self.calibration_step = 2
            time.sleep(0.05)
            self.metin_bot.stop(True, time.time(), 0, False)
            return
        # time.sleep(0.05)
        # self.zoom_out(out_time)



    ### CALIBRATION STOPS STATE ITSELF NOW YOU SHOULD NOT STOP THE STATE NOW AFTER THE CALIBRATION
    def calibrate_view(self, calibration_type="guard", ):
        #self.metin_bot.metin_window.activate()
        if self.calibration_step == 0:
            self.calibration_type = calibration_type
            self.metin_bot.is_calibrating = True
        # Camera option: Near, Perspective all the way to the right

        if self.calibration_type != "first_arena_middlepoint" and self.calibration_step == 0:
            time.sleep(0.05)
            self.metin_bot.osk_window.start_zooming_out()
            time.sleep(0.6)
            self.metin_bot.osk_window.stop_zooming_out()
            time.sleep(0.1)
            self.calibration_step = 2
            self.metin_bot.stop(True, time.time(), 0, False)
            return
        #self.osk_window.start_zooming_in()
        #self.calibration_step = 1
        #time.sleep(0.07)
        elif self.calibration_step == 0 or self.calibration_step == 1:
            time.sleep(0.05)
            self.zoom_in_out()
            return
        
        #time.sleep(0.07)
        if self.calibration_step == 2:
            time.sleep(0.05)
            self.metin_bot.osk_window.start_rotating_up()
            #time.sleep(1.1)
            time.sleep(0.05)
            windows_swap_fix(True)
            self.metin_bot.osk_window.stop_rotating_up()
            time.sleep(0.04)
            self.calibration_step = 3
            self.metin_bot.stop(True, time.time()+1.3, 0, False)
            return
        
        if self.calibration_step == 3:
            time.sleep(0.05)
            self.metin_bot.osk_window.start_rotating_down()
            #time.sleep(random.uniform(0.58, 0.63))
            if self.calibration_type == "first_arena":
                time.sleep(0.73)
            elif self.calibration_type == 'first_arena_middlepoint':
                time.sleep(0.62)
            elif self.calibration_type == "second_arena":
                time.sleep(0.7)
            else:
                time.sleep(random.uniform(0.62, 0.7))
            self.metin_bot.osk_window.stop_rotating_down()
            time.sleep(0.04)
            self.calibration_step = 0
            self.metin_bot.is_calibrating = False
            self.metin_bot.stop(True, time.time(), 0, True)
            return
        
        #self.zoom_out()
        # self.metin_bot.osk_window.calibrate_with_mouse(calibration_type)
        #self.osk_window.stop_zooming_in()

    def calibrate_view_after_dangeon(self):
        self.metin_bot.metin_window.activate()
        # Camera option: Near, Perspective all the way to the right
        # self.osk_window.start_rotating_up()
        # time.sleep(0.8)
        # self.osk_window.stop_rotating_up()
        # self.osk_window.start_rotating_down()
        # time.sleep(0.75)
        # self.osk_window.stop_rotating_down()
        # self.osk_window.start_zooming_out()
        # time.sleep(0.8)
        # self.osk_window.stop_zooming_out()
        self.metin_bot.osk_window.start_zooming_in()
        time.sleep(0.08)
        self.metin_bot.osk_window.stop_zooming_in()

    def rotate_view(self, small_rotation=False, big_rotation=False, rotate_right=False):
        self.metin_bot.osk_window.rotate_with_mouse(small_rotation, big_rotation, rotate_right)
        #self.osk_window.move_with_camera_rotation()

    def rotate_view_async(self, stop=False):
        self.metin_bot.osk_window.rotate(stop)

    def process_metin_info(self, text):
        # Remove certain substrings
        remove = ['\f', '.', '°', '%', '‘', ',']
        for char in remove:
            text = text.replace(char, '')

        # Replace certain substrings
        replace = [('\n', ' '), ('Lw', 'Lv'), ('Lv', 'Lv.')]
        for before, after in replace:
            text = text.replace(before, after)

        # '%' falsely detected as '96'
        p = re.compile('(?<=\d)96')
        m = p.search(text)
        if m:
            span = m.span()
            text = text[:span[0]]

        # Parse the string
        parts = text.split()
        parts = [part for part in parts if len(part) > 0]
        if len(parts) == 0:
            return None
        else:
            health_text = re.sub('[^0-9]', '', parts[-1])
            health = 9999
            if len(health_text) > 0:
                health = int(health_text)
            name = ' '.join(parts[:-1])
            return name, health

    def does_metin_exist_on_current_channel(self):
        self.metin_bot.osk_window.find_metin()
        time.sleep(0.1)
        chat_text = self.get_clicked_place_info((215,683),(812,732))
        possible_chat_texts = ["Na tej mapie nie ma Kamieni Metin do znalezienia.",
                               "Na te} mapie nie ma Kamiani Metin do znalezieria,",
                               "Na tej mapie nie ma Kamieni Metin do znalezienia,",
                               "Na tej mapie nie ma Kamieni Metin"]
        if chat_text is not None:
            metin_exists = True
            for text in possible_chat_texts:
                if text in chat_text:
                    metin_exists = False
            return metin_exists
        return True

    def get_mob_info(self):
        top_left = (300, 21)
        bottom_right = (700, 60)

        mob_info_box = self.metin_bot.vision.extract_section(self.metin_bot.get_screenshot_info(), top_left, bottom_right)

        mob_info_box = self.metin_bot.vision.apply_hsv_filter(mob_info_box, hsv_filter=self.metin_bot.mob_info_hsv_filter)
        mob_info_text = pytesseract.image_to_string(mob_info_box)

        return self.process_metin_info(mob_info_text)

    def get_mob_health(self):
        top_left = (550, 35)
        bottom_right = (700, 60)

        mob_info_box = self.metin_bot.vision.extract_section(self.metin_bot.get_screenshot_info(), top_left, bottom_right)

        mob_info_box = self.metin_bot.vision.apply_hsv_filter(mob_info_box, hsv_filter=self.metin_bot.mob_info_hsv_filter)
        mob_info_text = pytesseract.image_to_string(mob_info_box)

        results = self.process_metin_info(mob_info_text)
        if results is not None:
            return results[1]
        else:
            return None

    def get_clicked_place_info(self, top_left, bottom_right):
        # top_left = (300, 21)
        # bottom_right = (705, 60)

        mob_info_box = self.metin_bot.vision.extract_section(self.metin_bot.get_screenshot_info(), top_left, bottom_right)

        mob_info_box = self.metin_bot.vision.apply_hsv_filter(mob_info_box, hsv_filter=self.metin_bot.mob_info_hsv_filter)
        mob_info_text = pytesseract.image_to_string(mob_info_box)

        return mob_info_text
    
    def get_text_from_current_cursor_position(self, width=200, height=150):
        pos = self.metin_bot.metin_window.get_relative_mouse_pos()
        top_left = self.metin_bot.metin_window.limit_coordinate((int(pos[0] - width / 2), pos[1] - height))
        bottom_right = self.metin_bot.metin_window.limit_coordinate((int(pos[0] + width / 2), pos[1]))
        try:
            time.sleep(0.02)

            text = self.get_clicked_place_info(top_left, bottom_right)
            return text
        except Exception as e:
            print('e')

    



    def check_if_player_is_logged_out(self):
        top_left = (450, 509)
        bottom_right = (560, 549)
        try:
            logged_out_info = self.metin_bot.vision.extract_section(self.metin_bot.get_screenshot_info(), top_left, bottom_right)

            #logged_out_info = self.metin_bot.vision.apply_hsv_filter(logged_out_info, hsv_filter=self.metin_bot.mob_info_hsv_filter)
            logged_out_info = pytesseract.image_to_string(logged_out_info)
            #possible_logged_out_info = ["ZALOG", "TNOGUI"]
            #print(logged_out_info)
            if check_if_text_from_image_includes_the_text(logged_out_info, TEXTS_FOR_ACTION['login']) or self.metin_bot.login_state:
                # self.metin_bot.set_object_detector_state(False)
                
                #self.metin_bot.dangeon_actions.restart_class_props()
                print(logged_out_info)
                self.login_user()
                return True
            else:
                return False
                #return "user is logged in"
        except Exception as e:
            print(e)
            print("error z logowaniem ale essa")
            return False
        #return logged_out_info

    def click_inventory_stash_x(self, inventory_number):
        stashes_coords = [(876,388),(914,388), (955,388), (990, 388)]

        time.sleep(0.17)
        self.metin_bot.metin_window.mouse_move(stashes_coords[inventory_number-1][0], stashes_coords[inventory_number-1][1]) 
        time.sleep(0.04)
        self.metin_bot.metin_window.mouse_click()

    def rotate_using_space_before_click(self):
        time.sleep(0.05)
        self.metin_bot.osk_window.start_hitting()
        time.sleep(0.2)
        self.metin_bot.osk_window.rotate_forward()
        time.sleep(0.1)
        self.metin_bot.osk_window.stop_hitting()

    def login_user(self):
        #time.sleep(11)
        account_save_button = [(870,363),(870,400),(870,437),(870,474),(870,501),(870,538), (870, 575), (870, 612)]

        if self.metin_bot.login_state == False:
            self.metin_bot.metin_window.mouse_move(511,405)
            time.sleep(0.3)
            self.metin_bot.metin_window.mouse_click()
            time.sleep(0.1)
            self.metin_bot.metin_window.mouse_move(account_save_button[self.metin_bot.bot_id][0],account_save_button[self.metin_bot.bot_id][1])
            time.sleep(0.2)
            self.metin_bot.metin_window.mouse_click()
            time.sleep(0.1)
            self.metin_bot.login_time = time.time()
            self.metin_bot.login_state = True
            time.sleep(0.4)
            self.metin_bot.switch_state(self.metin_bot.state_order.get_logging_state())
            return

        #######
        elif self.metin_bot.login_state == True and time.time() - self.metin_bot.login_time > 10:
            time.sleep(0.1)
            self.metin_bot.osk_window.pick_x_champion_in_champion_select("2")
            time.sleep(0.2)
            self.metin_bot.metin_window.mouse_move(239,616)
            time.sleep(0.07)
            self.metin_bot.metin_window.mouse_click()
            time.sleep(0.4)
            if time.time() - self.metin_bot.login_time <= 25:
                self.metin_bot.stop()
                return

        ######
        
        if time.time() - self.metin_bot.login_time > 25:
            
            self.metin_bot.state_order.dangeon_actions.restart_class_props()
            self.metin_bot.state_order.dangeon_actions.tp_to_dangeon = True
            self.metin_bot.state_order.dangeon_actions.change_channel = True
            self.metin_bot.health_checks_bool = True
            self.metin_bot.login_state = False
            self.metin_bot.switch_state(self.metin_bot.state_order.get_initializing_state())
            return
        # self.check_if_player_is_logged_out()

    def tp_to_dangeon(self, tp_back=False):

        #self.metin_bot.metin_window.activate()

        #time.sleep(3)

        self.metin_bot.metin_window.mouse_move(521,208) #521, 247
        time.sleep(0.04)
        self.metin_bot.metin_window.mouse_click()

        time.sleep(1.5)
        #cv.imwrite("test.png", cv.cvtColor(self.metin_bot.get_screenshot_info(), cv.COLOR_RGB2BGR))
        x,y = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_dangeon_enter_the_dangeon_button(), 0.99)
        if x:
            self.metin_bot.metin_window.mouse_move(x,y)
            time.sleep(0.04)
            self.metin_bot.metin_window.mouse_click()
        #else:


        #time.sleep(4)

    def check_if_you_cannot_tp_to_dangeon(self):
        # top_left = (350, 215)
        # bottom_right = (669, 591)
        # modal_info = self.metin_bot.vision.extract_section(self.metin_bot.get_screenshot_info(), top_left, bottom_right)

        x,y = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_dangeon_you_cannot_enter_the_dangeon_button(), 0.99)
        if x:
            self.metin_bot.metin_window.mouse_move(x,y)
            time.sleep(0.04)
            self.metin_bot.metin_window.mouse_click()
            return True
        return False

    def tp_to_dangeon_again(self):
        self.metin_bot.metin_window.activate()

        time.sleep(0.07)
        self.metin_bot.metin_window.mouse_move(963,66)
        time.sleep(0.04)
        self.metin_bot.metin_window.mouse_click()
        time.sleep(0.1)
        self.metin_bot.osk_window.end_pick_up()
        time.sleep(0.2)
        
        self.metin_bot.metin_window.mouse_move(473, 403)
        time.sleep(0.04)
        self.metin_bot.metin_window.mouse_click()

    def turn_on_buffs(self, only_potions=False):
        #self.metin_bot.metin_window.activate()
        self.metin_bot.last_buff = time.time()
        if not only_potions:
            time.sleep(0.05)
            self.metin_bot.osk_window.un_mount()
            time.sleep(0.8)
            self.metin_bot.osk_window.activate_aura()
            #time.sleep(2)
            #self.osk_window.activate_berserk()
            time.sleep(0.32)
            self.metin_bot.osk_window.un_mount()
            time.sleep(0.08)
        self.metin_bot.osk_window.activate_buffs()

    # def send_telegram_message(self, msg):
    #     bot = telegram.Bot(token=bot_token)
    #     bot.sendMessage(chat_id=chat_id, text=msg)

    def teleport_to_x_respawn(self, tp_page, respawn):
       
        metin_tp_page = [(338,519),(455,518)]
        coords = [(718,272),(718,302), (718,331), (718, 363), (718, 392), (718, 421), (718,453), (718, 482), (718, 512)]

        time.sleep(0.2)
        self.metin_bot.osk_window.activate_teleports()

        time.sleep(0.15)
        self.metin_bot.metin_window.mouse_move(metin_tp_page[tp_page-1][0], metin_tp_page[tp_page-1][1])
        time.sleep(0.13)
        self.metin_bot.metin_window.mouse_click()

        time.sleep(0.12)
        self.metin_bot.metin_window.mouse_move(coords[respawn-1][0], coords[respawn-1][1])
        time.sleep(0.12)
        self.metin_bot.metin_window.mouse_click()
        time.sleep(0.09)
        self.metin_bot.metin_window.mouse_move(coords[respawn-1][0]+10, coords[respawn-1][1]+4)
        time.sleep(0.20)
        self.metin_bot.metin_window.mouse_click()
        time.sleep(0.07)
        #time.sleep(4)

    def teleport_to_next_metin_respawn(self, respawn_number=1):
       
        metin_tp_page = [(338,519),(455,518)]
        coords = [(718,272),(718,302), (718,331), (718, 363), (718, 392), (718, 421), (718,453), (718, 482), (718, 512)]

        self.metin_bot.metin_window.activate()
        self.metin_bot.osk_window.activate_teleports()

        time.sleep(0.1)
        self.metin_bot.metin_window.mouse_move(metin_tp_page[math.floor((self.metin_bot.metin_teleports_passed)/8) % 2][0], metin_tp_page[math.floor((self.metin_bot.metin_teleports_passed)/8) % 2][1])
        time.sleep(0.04)
        self.metin_bot.metin_window.mouse_click()

        time.sleep(0.1)
        self.metin_bot.metin_window.mouse_move(coords[(respawn_number-1)%8][0], coords[(respawn_number-1)%8][1])
        time.sleep(0.04)
        self.metin_bot.metin_window.mouse_click()
        #time.sleep(4)

    def change_channel(self, channel):
           
        self.metin_bot.metin_teleports_passed = 0

        channel_cords = [(896,40), (893,63), (896,84), (900, 102), (910,121), (931,131), (952,136), (973,130)]

        #self.metin_bot.metin_window.activate()

        time.sleep(0.2)
        self.metin_bot.metin_window.mouse_move(channel_cords[channel-1][0], channel_cords[channel-1][1])
        time.sleep(0.1)
        self.metin_bot.metin_window.mouse_click()
        time.sleep(0.1)
        #time.sleep(9)
        #self.metin_bot.osk_window.heal_yourself()

    def change_metin_respawn_or_channel(self):
       
        if (self.metin_bot.metin_teleports_passed) % 16 == 15:
            self.metin_bot.current_metin_respawn = 0
            self.metin_bot.current_channel = (self.metin_bot.current_channel % 8) + 1
            self.metin_bot.osk_window.heal_yourself()
            self.change_channel(self.metin_bot.current_channel)
            self.metin_bot.osk_window.heal_yourself()     
            self.metin_bot.osk_window.turn_poly_off()
            self.metin_bot.osk_window.turn_poly_on()
            self.metin_bot.current_metin_respawn = (self.metin_bot.current_metin_respawn % 16) + 1
            
            self.teleport_to_next_metin_respawn(self.metin_bot.current_metin_respawn, )

            self.metin_bot.metin_teleports_passed += 1

            self.calibrate_view()
        else:
            self.metin_bot.current_metin_respawn = (self.metin_bot.current_metin_respawn % 16) + 1
            self.teleport_to_next_metin_respawn(self.metin_bot.current_metin_respawn)
            self.metin_bot.metin_teleports_passed += 1

    def check_if_dead(self):
        respawn_text = self.get_clicked_place_info((65,70),(238,88))
        possible_texts = ["Rozpocenij tutaj", "tutaj", "Rozpocenij", "Rozpocznij"]

        if respawn_text is not None:
            respawn = False
            for text in possible_texts:
                if text in respawn_text:
                    respawn = True
            return respawn
        else: return False

    def respawn_if_dead(self):
        if self.check_if_dead():
            #time.sleep(10)
            time.sleep(0.2)
            self.metin_bot.metin_window.mouse_move(156,80)
            time.sleep(0.04)
            self.metin_bot.metin_window.mouse_click()
            time.sleep(0.5)
            self.metin_bot.osk_window.heal_yourself()
            time.sleep(0.1)
            self.metin_bot.osk_window.heal_yourself()
            time.sleep(0.2)
            self.metin_bot.osk_window.un_mount()
            time.sleep(0.4)
            return True
        return False

    def check_if_bot_is_stuck_in_dangeon(self, time_in_seconds):
        if time.time() - self.metin_bot.dangeon_entered_time > time_in_seconds:
            print("Bugged in dangeon while in: " + str(self.metin_bot.get_state().name) + " state" )
            self.metin_bot.state_order.dangeon_actions.restart_class_props()
            self.metin_bot.dangeon_entered_time = time.time()
            self.metin_bot.state_order.dangeon_actions.tp_to_dangeon = True
            self.metin_bot.state_order.dangeon_actions.change_channel = True
            self.metin_bot.health_checks_bool = True
            self.metin_bot.switch_state(self.metin_bot.state_order.get_initializing_state())
            return True
        return False

    def check_if_equipment_is_on(self):
        top_left = (840, 80)
        bottom_right = (1023, 160)

        eq_info = self.metin_bot.vision.extract_section(self.metin_bot.get_screenshot_info(), top_left, bottom_right)
        x,y = self.metin_bot.vision.find_image(eq_info, get_eq_ervelia_stripe(), 0.90)

        # eq_info = self.metin_bot.vision.apply_hsv_filter(eq_info, hsv_filter=self.metin_bot.mob_info_hsv_filter)
        # eq_info = pytesseract.image_to_string(eq_info)
        # # possible_logged_out_info = ["ZALOG", "TNOGUI"]
        # if "Ekw" in eq_info or "nek" in eq_info:
        #     return True
        # else:
        #     return False
        if x is not None:
            return True
        else:
            return False
        
    def open_inventory(self, tried=0):
        if not self.check_if_equipment_is_on():
            self.metin_bot.osk_window.open_inventory()

        ## NOW CHECK IF INVENTROY IS ON
        time_of_await_to_open_again = time.time() + 0.3
        while time.time() < time_of_await_to_open_again:
            if self.check_if_equipment_is_on():
                return
        
        if tried > 20:
            return
        
        self.open_inventory(tried+1)

    def close_inventory(self, tried=0):
        if self.check_if_equipment_is_on():
            self.metin_bot.osk_window.open_inventory()

        ## NOW CHECK IF INVENTROY IS ON
        time_of_await_to_close_again = time.time() + 0.3
        while time.time() < time_of_await_to_close_again:
            if not self.check_if_equipment_is_on():
                return
        
        if tried > 20:
            return

        self.close_inventory(tried+1)
                
        
    def collect_the_event_card_drop(self):
        #self.metin_bot.metin_window.activate()

        time.sleep(0.4)
        self.metin_bot.metin_window.mouse_move(570,490)
        time.sleep(0.04)
        self.metin_bot.metin_window.mouse_click()

        time.sleep(0.1)

    def check_if_player_is_on_the_mount(self):
        self.open_inventory()
        time.sleep(0.43)
        self.metin_bot.metin_window.mouse_move(951,161)
        time.sleep(0.07)
        self.metin_bot.metin_window.mouse_click()
        time.sleep(0.22)
        
        top_left = (629, 329)
        bottom_right = (676, 366)
        mount_box = self.metin_bot.vision.extract_section(self.metin_bot.get_screenshot_info(), top_left, bottom_right)
        x,y = self.metin_bot.vision.find_image(mount_box, get_empty_mount_image(), 0.90)
        
       
        self.metin_bot.metin_window.mouse_move(749,179)
        time.sleep(0.07)
        self.metin_bot.metin_window.mouse_click()
        time.sleep(0.05)
        self.close_inventory()
        if x is not None:
            return False
        else:
            return True
        
    def get_the_player_on_the_horse(self):
        if not self.check_if_player_is_on_the_mount():
            time.sleep(0.1)
            self.metin_bot.osk_window.un_mount()
            time.sleep(0.4)

    def health_checks(self, max_time_in_dang=600):
        try:
            if self.respawn_if_dead():
                return
            if self.check_if_bot_is_stuck_in_dangeon(max_time_in_dang):
                return
            if self.check_if_player_is_logged_out():
                return
           
        except Exception as e:
            print(e)
            print("health checks needs image first")

    def detect_gm(self):
        # print("DETECTION OF GM START")
        # print(time.time())
        image = self.metin_bot.get_screenshot_info()
        x,y = self.metin_bot.vision.find_image(image, gm_icon_image(), 0.80)
        
        top_left = (161, 17)
        bottom_right = (820, 255)
        image_cuted_for_detection = self.metin_bot.vision.extract_section(image, top_left, bottom_right)
        text = pytesseract.image_to_string(image_cuted_for_detection).lower()
        does_screen_contain_text = 'napisz' in text or "admin" in text or "wykryto" in text
        if x is not None or does_screen_contain_text:
            print("GM DETECTED MUSIC IS PLAYING")
            play_music()
        # print("DETECTION OF GM STOP")
        # print(time.time())

    def is_player_hitting_enemy(self):
        if self.metin_bot.started_moving_time is None:
            self.metin_bot.started_moving_time = time.time()
            self.metin_bot.moving_to_enemy_flag_clicked = False

        result = self.get_mob_info()
        #print(result[0])
        if result is not None and result[1] < 1000:
            self.metin_bot.started_moving_time = None
            return True
        elif time.time() - self.metin_bot.started_moving_time < 4.5:
            return self.is_player_hitting_enemy()
        else:
            self.metin_bot.started_moving_time = None
            return True

    def renew_alchemy(self):
        time.sleep(0.2)
        self.metin_bot.osk_window.open_alchemy()
        time.sleep(0.1)
        self.metin_bot.metin_window.mouse_move(622,172)
        time.sleep(0.12)
        self.metin_bot.metin_window.mouse_click()
        time.sleep(0.1)
        self.metin_bot.metin_window.mouse_move(474,409)
        time.sleep(0.12)
        self.metin_bot.metin_window.mouse_click()
        time.sleep(1)
        self.metin_bot.metin_window.mouse_move(505,409)
        time.sleep(0.12)
        self.metin_bot.metin_window.mouse_click()
        time.sleep(0.2)
        self.metin_bot.osk_window.open_alchemy()
        time.sleep(0.1)
    
    def remove_dangon_items_from_inv(self, images_path=ERVELIA_DANG30_IMAGE_PATHS):

        time.sleep(0.1)
        self.open_inventory()
        time.sleep(0.15)
        self.metin_bot.metin_window.mouse_move(793,211)
        time.sleep(0.08)
        self.metin_bot.metin_window.mouse_click()
        time.sleep(0.6)
        
        items_removed = 0

        for inv_page in [1,2,3,4]:

            self.click_inventory_stash_x(inv_page)
            time.sleep(0.2)

            merged_centers = []

            image = self.metin_bot.get_screenshot_info()
            top_left = (854, 386)
            bottom_right = (1017, 685)
            image_cuted_for_detection = self.metin_bot.vision.extract_section(image, top_left, bottom_right)

            for path in images_path.values():
                centers = self.metin_bot.vision.find_image(image_cuted_for_detection, path, 0.7, 30)
                centers = sorted(centers, key=lambda center: center[1])
                if len(centers) > 0:
                    merged_centers = merged_centers + centers


            items_clicked_indexes = []

            #merged_centers = merged_centers[:24]
            #print(merged_centers)

            merged_centers = sorted(merged_centers, key=lambda merged_center: merged_center[1])

            for count, value in enumerate(merged_centers):
                index_of_next_click = self.metin_bot.vision.index_of_centers_that_hasnt_been_clicked_yet(merged_centers, items_clicked_indexes, inv_page)
                if index_of_next_click is not None:
                    self.metin_bot.metin_window.mouse_move(merged_centers[index_of_next_click][0]+top_left[0],merged_centers[index_of_next_click][1]+top_left[1])
                    time.sleep(0.05)
                    self.metin_bot.metin_window.mouse_right_click()
                    time.sleep(0.03)
                    items_clicked_indexes.append([merged_centers[index_of_next_click][0], merged_centers[index_of_next_click][1], inv_page])
                    items_removed += 1
                    if items_removed % 24 == 0:
                        time.sleep(0.05)
                        self.metin_bot.metin_window.mouse_move(480,480)
                        time.sleep(0.05)
                        self.metin_bot.metin_window.mouse_click()
                        time.sleep(0.6)
            
        time.sleep(0.05)
        self.metin_bot.metin_window.mouse_move(480,480)
        time.sleep(0.05)
        self.metin_bot.metin_window.mouse_click()
        time.sleep(0.6)

        time.sleep(0.05)
        self.metin_bot.metin_window.mouse_move(600,281)
        time.sleep(0.05)
        self.metin_bot.metin_window.mouse_click()
        time.sleep(0.6)

        self.close_inventory()