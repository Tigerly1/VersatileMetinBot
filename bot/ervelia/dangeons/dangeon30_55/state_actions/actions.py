import enum
import random
import time
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.core_loop import MetinBot  # This import is only for type checking
from utils.helpers.paths import get_dangeon_item_dangeon30, get_first_area_dangeon30, get_second_area_dangeon30

class DangeonState(enum.Enum):
    ENTER_THE_DANGEON = 0
    FIRST_ARENA = 1
    KILL_MOBS = 2
    KILL_METINS = 3
    KILL_MINI_BOSS = 4
    SECOND_ARENA = 5
    GATHER_ITEMS = 6
    SECOND_METINS = 7
    SECOND_MINI_BOSS = 8
    END_BOSS = 9
    DEBUG = 10
    INITIALIZING = 999

LABELS = ['metin', 'boss', 'guard', 'first_arena', 'second_arena']

class Actions:
    def __init__(self, metin_bot: 'MetinBot'):
        self.metin_bot = metin_bot


        ### states to clear
        self.first_metins_killed = 0
        self.gather_items_time = 65
        self.items_gathered = 0
        self.inventory_page = 1
        self.second_metins_killed = 0
        self.detect_boss_tries = 5
        self.tp_to_dangeon = True
        self.change_channel = False

       
    
    def enter_the_dangeon(self):
        if self.metin_bot.dangeon_end_time > time.time() - 60 and self.metin_bot.dangeons_count > 0:
            self.metin_bot.game_actions.tp_to_dangeon_again()
        else:
            if self.tp_to_dangeon:
                self.metin_bot.game_actions.teleport_to_x_respawn(1,1)
                self.tp_to_dangeon = False
            if self.change_channel:
                self.metin_bot.current_channel = (self.metin_bot.current_channel % 8) + 1
                self.metin_bot.game_actions.change_channel(self.metin_bot.current_channel)
                self.change_channel = False
            next_action = self.metin_bot.detect_and_click('guard')
            if not next_action:
                return
            self.metin_bot.game_actions.tp_to_dangeon()
        self.metin_bot.dangeon_entered_time = time.time()
        # code to enter the dungeon
        time.sleep(4)
        self.metin_bot.game_actions.calibrate_view()
        self.metin_bot.increment_state()
    
    def first_arena(self):

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
      
        time.sleep(1.3)
        self.metin_bot.osk_window.activate_horse_dodge()
        time.sleep(2)
        # code to move to the next room
        self.metin_bot.increment_state()

    def kill_mobs(self):
        time.sleep(1)
        self.metin_bot.game_actions.turn_on_buffs()
        time.sleep(0.05)
        self.metin_bot.osk_window.start_hitting()
        time.sleep(0.03)

        self.metin_bot.osk_window.pull_mobs()
        time.sleep(0.2)

        time.sleep(13)
        self.metin_bot.osk_window.stop_hitting()
        # code to attack the monster
        self.metin_bot.increment_state()
    
    def kill_metins(self):
        if self.first_metins_killed < 4 and self.metin_bot.time_entered_state + 35 > time.time():
            is_clicked = self.metin_bot.detect_and_click('metin', True)
            if is_clicked:
                #time.sleep(5)
                self.first_metins_killed += 1
        else:
            self.metin_bot.increment_state()

        # code to use a skill
    
    def kill_mini_boss(self):
        time.sleep(0.05)
        self.metin_bot.osk_window.start_hitting()
        time.sleep(0.03)

        self.metin_bot.osk_window.pull_mobs()
        time.sleep(0.2)

        time.sleep(13)
        self.metin_bot.osk_window.pull_mobs()
        time.sleep(11)
        self.metin_bot.osk_window.stop_hitting()

        # code to attack the monster
        self.metin_bot.increment_state()
        

    def second_arena(self):
        # x, y = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_second_area_dangeon30(), 0.25)
        # if x is None:
        #     self.metin_bot.game_actions.rotate_view()
        #     random_number = random.random()
        #     # 15% success rate
        #     if random_number <= 0.1:
        #         self.metin_bot.game_actions.calibrate_view()
        # else:
        next_action = self.metin_bot.detect_and_click('second_arena')
        if not next_action:
            return
        # while True:
        #     next_action = self.metin_bot.detect_and_click('second_arena')
        #     if next_action:
        #         break

        time.sleep(1)
        self.metin_bot.osk_window.activate_horse_dodge()
        time.sleep(2)
        # code to move to the next room
        self.metin_bot.increment_state()
        # code to move to the next room

    def gather_items(self):
        time.sleep(0.5)
        self.metin_bot.osk_window.start_hitting()
        while self.gather_items_time > 0:

            self.metin_bot.osk_window.pull_mobs()
            time.sleep(2)
            self.gather_items_time = self.gather_items_time - 2
        time.sleep(1)
        if not self.metin_bot.game_actions.check_if_equipment_is_on():
            self.metin_bot.osk_window.open_inventory()

        while self.items_gathered < 4:
            x, y = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_dangeon_item_dangeon30(), 0.6)
            if x is None:
                self.metin_bot.osk_window.pull_mobs()
                self.inventory_page = (self.inventory_page % 4) + 1
                self.metin_bot.game_actions.click_inventory_stash_x(self.inventory_page)
                time.sleep(0.3)
            else:
                self.metin_bot.metin_window.mouse_move(x,y)
                time.sleep(0.3)
                self.metin_bot.metin_window.mouse_right_click()
                time.sleep(0.6)
                self.items_gathered += 1
        
        self.metin_bot.osk_window.stop_hitting()
        time.sleep(0.3)
        self.metin_bot.osk_window.open_inventory()
        time.sleep(0.2)
        self.metin_bot.game_actions.turn_on_buffs()
        self.metin_bot.increment_state()

    def second_metins(self):
        if self.second_metins_killed < 4 and self.metin_bot.time_entered_state + 35 > time.time():
                is_clicked = self.metin_bot.detect_and_click('metin', True)
                if is_clicked:
                    #time.sleep(5)
                    self.second_metins_killed += 1
        else:
            self.metin_bot.osk_window.start_hitting()
            time.sleep(0.8)
            self.metin_bot.increment_state()

    def second_mini_boss(self):
       
        
        self.metin_bot.osk_window.pull_mobs()
        time.sleep(0.2)

        if self.metin_bot.time_entered_state + 15 <= time.time() and (self.metin_bot.detection_result is not None and "boss" in self.metin_bot.detection_result['labels']):

            self.metin_bot.osk_window.stop_hitting()
            time.sleep(1)
            self.metin_bot.increment_state()



        elif self.metin_bot.time_entered_state + 27 <= time.time():
        
            self.metin_bot.osk_window.stop_hitting()
            time.sleep(1)
            self.metin_bot.increment_state()

        # code to attack the monster

    def end_boss(self):
        # is_clicked = False
        # while self.detect_boss_tries > 0:
        #     is_clicked = self.metin_bot.detect_and_click('boss')
        #     if is_clicked:
        #         time.sleep(14)
        #     else:
        #         self.metin_bot.game_actions.rotate_view()
        #         self.detect_boss_tries -= 1

        # if not is_clicked:
        time.sleep(0.05)
        self.metin_bot.osk_window.start_hitting()
        time.sleep(16)
        self.metin_bot.osk_window.stop_hitting()

        self.metin_bot.dangeon_end_time = time.time()
        print("dangeon finished in {} minutes".format((self.metin_bot.dangeon_end_time - self.metin_bot.dangeon_entered_time) / 60))
        self.metin_bot.osk_window.pick_up()
        
        self.restart_class_props()

        self.metin_bot.dangeons_count += 1
        # code to loot items
        self.metin_bot.increment_state()


    def debug(self):
        # code to loot items
        pass

    def restart_class_props(self):
        self.first_metins_killed = 0
        self.gather_items_time = 80
        self.items_gathered = 0
        self.inventory_page = 1
        self.second_metins_killed = 0
        self.detect_boss_tries = 5
