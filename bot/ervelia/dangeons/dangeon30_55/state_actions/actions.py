import enum
import random
import time
from typing import TYPE_CHECKING
from bot.ervelia.dangeons.dangeon30_55.state import DangeonState
if TYPE_CHECKING:
    from bot.core_loop import MetinBot  # This import is only for type checking
from utils.helpers.paths import get_dangeon_end_image, get_dangeon_item_dangeon30, get_first_area_dangeon30, get_second_area_dangeon30



LABELS = ['metin', 'boss', 'guard', 'first_arena', 'second_arena']

class Actions:
    def __init__(self, metin_bot: 'MetinBot'):
        self.metin_bot = metin_bot


        ### states to clear
        self.first_metins_killed = 0
        self.gather_items_time = 100
        self.items_gathered = 0
        self.inventory_page = 1
        self.second_metins_killed = 0
        self.detect_boss_tries = 5
        self.tp_to_dangeon = True
        self.change_channel = False
        self.start_of_the_action_time = None
        self.metin_start_hitting_time = None
        self.max_metins_rotations = 50
        self.metins_rotation = 0

    def enter_the_dangeon(self):
       

        if self.metin_bot.dangeon_end_time > time.time() - 60 and self.metin_bot.dangeons_count > 0 and self.tp_to_dangeon == False:
            self.metin_bot.game_actions.tp_to_dangeon_again()
            time.sleep(0.1)
        else:
            if self.tp_to_dangeon:
                self.metin_bot.game_actions.teleport_to_x_respawn(1,1)
                self.tp_to_dangeon = False
                self.metin_bot.stop()
                time.sleep(0.1)
                return 
            if self.change_channel:
                time.sleep(4)
                self.metin_bot.current_channel = (self.metin_bot.current_channel % 8) + 1
                self.metin_bot.game_actions.change_channel(self.metin_bot.current_channel)
                self.change_channel = False
                self.metin_bot.stop()
                time.sleep(0.1)
                return
            # if self.start_of_the_action_time is None:
            #     self.start_of_the_action_time = time.time()
            # if time.time() - self.start_of_the_action_time > 10:
            #     self.metin_bot.game_actions.calibrate_view("first_arena")
            #     self.tp_to_dangeon = True
            #     self.start_of_the_action_time = None
            #     self.metin_bot.stop()
            #     return
            next_action = self.metin_bot.detect_and_click('guard')
            if not next_action:
                return
            self.metin_bot.game_actions.tp_to_dangeon()
        self.metin_bot.dangeon_entered_time = time.time()
        # code to enter the dungeon
        self.start_of_the_action_time = None
        time.sleep(0.1)
        self.metin_bot.increment_state()
    
    def first_arena(self):
        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
            self.metin_bot.game_actions.calibrate_view("first_arena")
        if time.time() - self.start_of_the_action_time > 120:
            self.start_of_the_action_time = None
            self.restart_after_action_not_changed()
            return
        next_action = self.metin_bot.detect_and_click('first_arena', rotate_before_click=True)
        if not next_action:
            return
        # # x, y = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_first_area_dangeon30(), 0.25)
        # # if x is None:
        # #     self.metin_bot.game_actions.rotate_view()
        # #     random_number = random.random()
        # #     # 15% success rate
        # #     if random_number <= 0.1:
        # #         self.metin_bot.game_actions.calibrate_view()
        # # else:

        time.sleep(0.5)
        #self.metin_bot.osk_window.activate_horse_dodge()
        time.sleep(2)
        # code to move to the next room
        self.start_of_the_action_time = None
        self.metin_bot.increment_state(False)

    def kill_mobs(self):
        
        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
            time.sleep(0.2)
            self.metin_bot.osk_window.start_hitting()
            time.sleep(0.03)
            self.metin_bot.osk_window.pull_mobs()
            time.sleep(0.3)
            self.metin_bot.stop()
            return

        self.metin_bot.osk_window.start_hitting()
        time.sleep(0.1)
        self.metin_bot.osk_window.pull_mobs()
        time.sleep(0.5)
        
        if time.time() - self.start_of_the_action_time > 15:   
            self.metin_bot.osk_window.stop_hitting()
            # code to attack the monster
            self.start_of_the_action_time = None
            self.metin_bot.increment_state(False)
        
    
    def kill_metins(self):
        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
            time.sleep(0.05)
            self.metin_bot.game_actions.turn_on_buffs()
            time.sleep(0.3)
        
        if self.first_metins_killed < 4  and self.metins_rotation <= self.max_metins_rotations:
            if self.metin_start_hitting_time is None or time.time() - self.metin_start_hitting_time > 9:
                is_clicked = self.metin_bot.detect_and_click('metin', True)
                self.metins_rotation += 1
                if is_clicked:
                    self.metin_start_hitting_time = time.time()
                    
                    #time.sleep(5)
                    self.metin_bot.stop()
                    self.first_metins_killed += 1
            else:
                self.metin_bot.stop()
        else:
            self.metins_rotation = 0
            self.metin_start_hitting_time = None
            self.start_of_the_action_time = None
            time.sleep(1.5)
            self.metin_bot.increment_state(False)

        # code to use a skill
    
    def kill_mini_boss(self):
        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
            time.sleep(0.2)
            self.metin_bot.game_actions.turn_on_buffs()
            time.sleep(0.3)
            self.metin_bot.osk_window.start_hitting()
            time.sleep(0.1)
            self.metin_bot.osk_window.pull_mobs()
            time.sleep(0.35)
            self.metin_bot.stop()
            return 
        self.metin_bot.osk_window.start_hitting()
        time.sleep(0.3)
        # self.metin_bot.osk_window.pull_mobs()
        # time.sleep(0.05)
        
        if time.time() - self.start_of_the_action_time > 34:
            self.metin_bot.osk_window.stop_hitting()
            # code to attack the monster
            self.start_of_the_action_time = None
            self.metin_bot.increment_state(False)
        elif time.time() - self.start_of_the_action_time > 13:
            self.metin_bot.osk_window.pull_mobs()
            time.sleep(0.2)
            self.metin_bot.stop()
        elif time.time() - self.start_of_the_action_time > 19:
            self.metin_bot.osk_window.pull_mobs()
            time.sleep(0.2)
            self.metin_bot.stop()
        else:
            self.metin_bot.stop()

        

    def second_arena(self):
        # x, y = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_second_area_dangeon30(), 0.25)
        # if x is None:
        #     self.metin_bot.game_actions.rotate_view()
        #     random_number = random.random()
        #     # 15% success rate
        #     if random_number <= 0.1:
        #         self.metin_bot.game_actions.calibrate_view()
        # else:
        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
        if time.time() - self.start_of_the_action_time > 150:
            self.restart_after_action_not_changed()
            self.metin_bot.stop()
            return
        next_action = self.metin_bot.detect_and_click('second_arena')
        if not next_action:
            return
        # while True:
        #     next_action = self.metin_bot.detect_and_click('second_arena')
        #     if next_action:
        #         break

        time.sleep(0.4)
        
        time.sleep(2)
        # code to move to the next room
        self.start_of_the_action_time = None
        self.metin_bot.increment_state(False)
        # code to move to the next room

    def gather_items(self):
        if self.start_of_the_action_time is None:
            self.metin_bot.osk_window.start_hitting()
            self.start_of_the_action_time = time.time()
            time.sleep(0.2)
            if not self.metin_bot.game_actions.check_if_equipment_is_on():
                self.metin_bot.osk_window.open_inventory()
        self.metin_bot.osk_window.start_hitting()
        time.sleep(0.03)
        self.metin_bot.osk_window.pull_mobs()
        time.sleep(0.05)
        if time.time() - self.start_of_the_action_time < self.gather_items_time:
            self.metin_bot.stop()
            return
        
        if self.items_gathered < 4:
            x, y = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_dangeon_item_dangeon30(), 0.6)
            if x is None:
                self.metin_bot.osk_window.pull_mobs()
                self.inventory_page = (self.inventory_page % 4) + 1
                self.metin_bot.game_actions.click_inventory_stash_x(self.inventory_page)
                time.sleep(0.3)
                if self.inventory_page == 1:
                    if not self.metin_bot.game_actions.check_if_equipment_is_on():
                        self.metin_bot.osk_window.open_inventory()
                    time.sleep(0.1)
                    self.metin_bot.stop()
            else:
                if self.items_gathered == 3:
                    self.metin_bot.osk_window.stop_hitting()
                    time.sleep(0.4)
                self.metin_bot.metin_window.mouse_move(x,y)
                time.sleep(0.3)
                self.metin_bot.metin_window.mouse_right_click()
                time.sleep(0.6)
                self.items_gathered += 1

        if self.items_gathered > 3:
          
            self.metin_bot.osk_window.open_inventory() #close inventory
            time.sleep(0.2)
            self.start_of_the_action_time = None
            self.metin_bot.game_actions.turn_on_buffs()
            time.sleep(1)
            self.metin_bot.increment_state(False)

    def second_metins(self):
        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
        
        if  self.second_metins_killed < 4 and self.metins_rotation <= self.max_metins_rotations:
            if self.metin_start_hitting_time is None or time.time() - self.metin_start_hitting_time > 8:
                is_clicked = self.metin_bot.detect_and_click('metin', True)
                self.metins_rotation += 1
                if is_clicked:
                    self.metin_start_hitting_time = time.time()
                    self.metins_rotation = 0
                    #time.sleep(5)
                    self.metin_bot.stop()
                    self.second_metins_killed += 1
            else:
                self.metin_bot.stop()

        else:
        # if self.second_metins_killed  >= 4 or self.metins_rotation > self.max_metins_rotations:
            self.metins_rotation = 0
            self.metin_start_hitting_time = None
            self.start_of_the_action_time = None
            time.sleep(2)
            self.metin_bot.increment_state(False)

    def second_mini_boss(self):
       
        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
            time.sleep(0.2)
            self.metin_bot.osk_window.start_hitting()
            time.sleep(0.2)
            self.metin_bot.game_actions.turn_on_buffs()
            time.sleep(0.4)
            self.metin_bot.osk_window.pull_mobs()
            time.sleep(0.05)
            self.metin_bot.stop()
            return
        
        self.metin_bot.osk_window.start_hitting()
        time.sleep(0.03)
        self.metin_bot.osk_window.pull_mobs()
        time.sleep(0.2)

        if self.start_of_the_action_time + 15 <= time.time() and (self.metin_bot.detection_result is not None and "boss" in self.metin_bot.detection_result['labels']):
            self.start_of_the_action_time = None
            time.sleep(0.5)
            self.metin_bot.increment_state(False)
        # BOS ZNIKL Z PLANETY ZIEMIA W TYM MIEJSCU
 
        elif self.start_of_the_action_time + 28 <= time.time():
            self.start_of_the_action_time = None
            time.sleep(0.5)
            self.metin_bot.increment_state(False)

        else:
            x, y = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_dangeon_end_image(), 0.9)
            if x is not None:
                self.metin_bot.increment_state(False)
            top_left = (300, 21)
            bottom_right = (700, 60)
            mob_text = self.metin_bot.game_actions.get_clicked_place_info(top_left, bottom_right)
            if "Prymus Myrow" in mob_text:
                 result = self.metin_bot.game_actions.get_mob_info()
                 if result is not None and result[1] < 200:
                     time.sleep(4)
                 self.metin_bot.increment_state(False)
            else:

                self.metin_bot.stop()
        # code to attack the monster

    def end_boss(self):
       
        top_left = (300, 21)
        bottom_right = (700, 60)
        mob_text = self.metin_bot.game_actions.get_clicked_place_info(top_left, bottom_right)
        if "Prymus Myrow" in mob_text:
            result = self.metin_bot.game_actions.get_mob_info()
            if result is not None and result[1] < 200:
                time.sleep(4)
        x, y = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_dangeon_end_image(), 0.9)
        if x is not None:
            self.start_of_the_action_time = time.time() - 26
        self.metin_bot.osk_window.start_hitting()
        time.sleep(0.03)
        self.metin_bot.osk_window.pull_mobs()
        time.sleep(0.2)

        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
            time.sleep(0.2)
            self.metin_bot.osk_window.start_hitting()
            time.sleep(0.03)
            self.metin_bot.osk_window.pull_mobs()
            time.sleep(0.05)
            self.metin_bot.stop()

        if self.start_of_the_action_time + 24 <= time.time():
            self.start_of_the_action_time = None
            time.sleep(0.2)
            self.metin_bot.osk_window.stop_hitting()
            self.metin_bot.dangeon_end_time = time.time()
            self.metin_bot.dangeons_count += 1
            print("Avarage time per dangeon {} seconds".format((time.time() - self.metin_bot.started) / self.metin_bot.dangeons_count))
            print("{} dangeon ended".format(self.metin_bot.dangeons_count))
            print("dangeon finished in {} minutes".format((self.metin_bot.dangeon_end_time - self.metin_bot.dangeon_entered_time) / 60))
            self.metin_bot.osk_window.pick_up()
            
            self.metin_bot.game_actions.collect_the_event_card_drop()

            x, y = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_dangeon_end_image(), 0.9)
            if x is None:
                self.tp_to_dangeon = True
            self.restart_class_props()

            
            # code to loot items
            self.metin_bot.increment_state(False)
        else:
            self.metin_bot.stop()


    def debug(self):
        # code to loot items
        pass

    def restart_class_props(self):
        self.first_metins_killed = 0
        self.gather_items_time = 100
        self.items_gathered = 0
        self.inventory_page = 1
        self.second_metins_killed = 0
        self.detect_boss_tries = 5
        self.start_of_the_action_time = None
        self.metin_start_hitting_time = None
        self.metins_rotation = 0

        if self.metin_bot.game_actions.check_if_equipment_is_on():
            self.metin_bot.osk_window.open_inventory()
        # time.sleep(0.1)
        # self.metin_bot.osk_window.escape_key()
        # time.sleep(0.1)
        # self.metin_bot.osk_window.escape_key()


    def restart_after_action_not_changed(self):
        self.restart_class_props()
        #self.metin_bot.dangeon_entered_time = time.time()
        self.tp_to_dangeon = True
        self.change_channel = True
        self.metin_bot.switch_state(DangeonState.INITIALIZING)
