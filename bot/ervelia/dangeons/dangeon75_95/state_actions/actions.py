import enum
import random
import time
from typing import TYPE_CHECKING
from bot.ervelia.dangeons.dangeon75_95.state import DangeonState
from bot.stats.dangeon import DungeonBotStatistics
if TYPE_CHECKING:
    from bot.core_loop import MetinBot  # This import is only for type checking
from utils.helpers.paths import get_dangeon_end_image, get_dangeon_item_dangeon30, get_first_area_dangeon30, get_second_area_dangeon30

import logging

# Configure logging
logging.basicConfig(filename="debug", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


LABELS = ['guard', 'first_arena_middlepoint', 'first_arena', 'second_arena', 'third_arena', 'metin']

class Actions:
    def __init__(self, metin_bot: 'MetinBot'):
        self.metin_bot = metin_bot


        ### states to clear
        
        self.arena_middlepoint = False
        self.metins_killed = 0
        self.picture_for_comparison = None
        self.gather_items_time = 102
        self.last_inventory_page_used = 1
        self.gather_items_stones_click = []
        self.items_gathered = 0
        self.inventory_page = 1
        self.detect_boss_tries = 5
        self.tp_to_dangeon = True
        self.change_channel = False
        self.metin_is_getting_killed = False
        self.metin_click_delayed = False
        self.metin_have_been_killed = False
        self.start_of_the_action_time = None
        self.horse_dodge_after_entering_arena = False
        self.metin_start_hitting_time = None
        self.pick_up_stop = False
        self.max_metins_rotations = 25
        self.min_metins_rotations = 7
        self.metins_rotation = 0
        self.guard_clicked = False

        self.stats = DungeonBotStatistics()

    def enter_the_dangeon(self):
       
        if self.metin_bot.dangeon_end_time > time.time() - 20 and self.metin_bot.dangeons_count > 0 and self.tp_to_dangeon == False:
            self.metin_bot.game_actions.tp_to_dangeon_again()
            self.metin_bot.dangeon_entered_time = time.time()
            self.start_of_the_action_time = None
            time.sleep(0.01)
            self.metin_bot.increment_state(False)
            return
            
        elif not self.guard_clicked:
            if self.tp_to_dangeon:
                self.metin_bot.game_actions.teleport_to_x_respawn(1,1)
                self.tp_to_dangeon = False
                self.metin_bot.stop(True, time.time()+5)
                return 
            if self.change_channel:
                self.metin_bot.game_actions.close_inventory()
                self.metin_bot.current_channel = (self.metin_bot.current_channel % 8) + 1
                self.metin_bot.game_actions.change_channel(self.metin_bot.current_channel)
                self.change_channel = False
                self.inventory_page = 1
                self.metin_bot.stop(True, time.time()+10)
                return
            
            if self.start_of_the_action_time is None:
                self.start_of_the_action_time = time.time()
            
            self.guard_clicked = self.metin_bot.detect_and_click('guard', True)

            if not self.guard_clicked:
                
                if random.random() < 0.04: 
                    self.metin_bot.game_actions.calibrate_view("guard")
                    self.start_of_the_action_time = None
                    self.metin_bot.stop()
                    return
                if random.random() < 0.01:
                    self.tp_to_dangeon = True
                    self.start_of_the_action_time = None
                    self.metin_bot.health_checks_bool = True
                    self.metin_bot.stop()
                    return

                if time.time() - self.start_of_the_action_time > 1:
                    self.start_of_the_action_time = None
                    self.metin_bot.stop()
                return
            self.metin_bot.stop(True, time.time()+3)
            return
        else:
            self.metin_bot.game_actions.tp_to_dangeon()

        self.metin_bot.dangeon_entered_time = time.time()
        self.start_of_the_action_time = None
        time.sleep(0.01)
        self.metin_bot.increment_state(True, time.time()+3)
    

    def enter_arena(self, arena):
        if self.start_of_the_action_time is None:
            self.enter_arena_calibration = False
            if arena == "first_arena":
                self.metin_bot.game_actions.calibrate_view("first_arena_middlepoint")
                #self.arena_middlepoint = True
                if self.metin_bot.game_actions.check_if_you_cannot_tp_to_dangeon():
                    self.start_of_the_action_time = None
                    self.restart_after_action_not_changed()
                    return
                
            self.start_of_the_action_time = time.time()

        if arena == "first_arena":
            if self.arena_middlepoint is None or self.arena_middlepoint == False:
                    result = self.enter_arena("first_arena_middlepoint")
                    if result == True:
                        self.arena_middlepoint = True
                        #self.start_of_the_action_time = None
                        self.metin_bot.stop(True, time.time()+3)
                    return
            else:
                self.metin_bot.osk_window.hold_key("t")

        if time.time() - self.start_of_the_action_time > 120:
            self.start_of_the_action_time = None
            self.restart_after_action_not_changed()
            return

        if time.time() - self.start_of_the_action_time > 40 and not self.enter_arena_calibration:
            if arena == "first_arena":
                self.metin_bot.osk_window.free_key("t") 
                if time.time() - self.start_of_the_action_time > 80:
                    self.metin_bot.game_actions.calibrate_view(arena)
            else:
                self.metin_bot.game_actions.calibrate_view(arena)
            self.enter_arena_calibration = True
            self.metin_bot.stop(True, time.time())
            return
        #print(arena)
       

        self.rotate_start_time = time.time()

        while time.time() - self.rotate_start_time  < 1:
            if arena == "first_arena":
                small_rotation = True if time.time() - self.start_of_the_action_time <= 65 else False
                result = self.metin_bot.brief_detection(arena, small_rotation=small_rotation, rotate_right=True)
            else:
                result = self.metin_bot.brief_detection(arena)
            if result:
                break
        
        if not result:
            if arena == "first_arena":
                self.metin_bot.osk_window.free_key("t")
            self.metin_bot.stop(True, time.time())
            return
        new_click = False
        if result:
            #if arena == "first_arena":
                #self.metin_bot.osk_window.free_key(" t")
            for x in range(0, 2):
                time.sleep(0.07)
                new_click = self.metin_bot.detect_and_click(arena, rotate_before_click=True, small_rotation=True)
                if new_click:
                    break
            if not new_click:
                if arena == "first_arena":
                    self.metin_bot.osk_window.free_key("t")
                self.metin_bot.stop(True, time.time())
                return
        if not result:
            if arena == "first_arena":
                self.metin_bot.osk_window.free_key("t")    
            self.metin_bot.stop(True, time.time())
            return
        if new_click and arena != "first_arena_middlepoint":
            self.start_of_the_action_time = None
            #self.metin_bot.increment_state(True, time.time()+5)
            time_for_entering_the_middle = 3.5
            if arena == "first_arena":
                self.metin_bot.osk_window.free_key("t")
                
                time.sleep(0.4)
                #self.metin_bot.game_actions.calibrate_view("second_arena")
                self.metin_bot.game_actions.zoom_out()
                time_for_entering_the_middle = 1.8
                self.horse_dodge_after_entering_arena = True
                #self.metin_bot.osk_window.activate_horse_dodge()
            elif arena == "third_arena":
                time_for_entering_the_middle = 2.6
                time.sleep(0.3)
                #self.horse_dodge_after_entering_arena = True
                self.metin_bot.osk_window.activate_horse_dodge()
                #time.sleep(2.0)
            # else:
                #time.sleep(3.5)
            self.metin_bot.increment_state(True, time.time()+time_for_entering_the_middle, priority=4, newest_detection_needed=False)
            return True
        elif new_click:
            return True

    def kill_mobs(self, time_to_kill=11, time_of_pull_stop=5, increment_state=True):
        if self.horse_dodge_after_entering_arena == True:
            time.sleep(0.02)
            self.metin_bot.osk_window.activate_horse_dodge()
            self.horse_dodge_after_entering_arena = False
            self.metin_bot.stop(True, time.time()+2, priority=5, newest_detection_needed=False)
            return

        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
            time.sleep(0.1)
            self.metin_bot.osk_window.start_hitting()
            time.sleep(0.09)
            self.metin_bot.osk_window.pull_mobs()
            time.sleep(0.15)
            self.metin_bot.osk_window.pull_mobs_different_version()
            time.sleep(0.04)
            self.metin_bot.stop(True, time.time()+time_of_pull_stop, newest_detection_needed=False)
            return
        
        time.sleep(0.05)
        self.metin_bot.osk_window.start_hitting()
        time.sleep(0.01)
        self.metin_bot.osk_window.pull_mobs()
        time.sleep(0.15)

        if time.time() - self.start_of_the_action_time > time_to_kill:   
            self.metin_bot.osk_window.stop_hitting()
            self.start_of_the_action_time = None
            if increment_state:
                self.metin_bot.increment_state(False)
            else:
                self.metin_bot.stop()
        else:
            self.metin_bot.stop(True, time.time()+13, newest_detection_needed=False)
    
    def kill_metins(self, number_of_metins, enemy_after_kill=False, detection_acc = 0.67, random_choice=False):

        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
            time.sleep(0.05)
            self.metin_bot.game_actions.turn_on_buffs()
            time.sleep(0.1)


        if enemy_after_kill and self.metin_have_been_killed:
            self.metin_bot.osk_window.start_hitting()
            time.sleep(0.06)
            # self.metin_bot.osk_window.pull_mobs()
            # time.sleep(0.15)
            self.metin_have_been_killed = False
            self.metin_bot.stop(True, time.time()+2.5)
            return
        
        
        if self.metin_bot.moving_to_enemy_flag_clicked or enemy_after_kill:
            self.metin_bot.osk_window.stop_hitting()


        if self.metin_click_delayed:
            self.metin_click_delayed = False
            self.metins_killed += 1
            self.metin_bot.stop(True, time.time()+8)
            return
       
        look_for_less_metins = 1 if enemy_after_kill else 0
        
        first_assumption = (self.metins_killed < (number_of_metins-look_for_less_metins)  and self.metins_rotation <= self.max_metins_rotations)
        second_assumption = self.metin_bot.get_top_center_position('metin', 0.5) is not None and self.metins_killed < 2 * number_of_metins
        third_assumption = self.min_metins_rotations >= self.metins_rotation

        check_match = True if enemy_after_kill else False

        #if self.metins_killed > 0:
        if self.metin_is_getting_killed:

            #self.metin_bot.osk_window.start_hitting()
            if not self.metin_bot.moving_to_enemy():
                self.metin_is_getting_killed = False
                self.metin_have_been_killed = True
                return
            
            else:
                ## metin will be probably killed there
                self.metins_killed += 1
                self.metin_click_delayed = True
                self.metin_bot.stop(True, time.time()+8)
                return

        # if self.metins_killed > number_of_metins-1 and not second_assumption:
        #     self.metin_bot.osk_window.rotate_with_mouse(False,True)
        #     time.sleep(0.12)

        if first_assumption or second_assumption or third_assumption:
            #if second_assumption and not first_assumption:
                 #self.metin_bot.osk_window.activate_flag()
                 #self.metin_bot.osk_window.activate_horse_dodge()
            time.sleep(0.05)

            chose_random_metin = False
            if random_choice and self.metins_killed > number_of_metins:
                self.metin_bot.osk_window.rotate_with_mouse(False,True)
                time.sleep(0.12)
                chose_random_metin = True

            is_clicked = self.metin_bot.detect_and_click('metin', metin_acc=detection_acc, check_match=check_match, chose_random=chose_random_metin)
            self.metins_rotation += 1
            if is_clicked:
                
                # if enemy_after_kill:
                #     time.sleep(0.2)
                #     self.metin_bot.osk_window.activate_horse_dodge()
                # if self.metins_killed < 2:
                #     time.sleep(0.2)
                    #self.metin_bot.osk_window.activate_horse_dodge()
                    #self.metin_bot.osk_window.activate_flag()
                if enemy_after_kill:
                    # if self.metin_bot.game_actions.is_player_hitting_enemy():
                        #self.metin_bot.osk_window.start_hitting()
                        self.metins_rotation = 0
                        self.metins_killed += 1
                        self.metin_have_been_killed = True
                        self.metin_bot.stop(True, time.time()+6.0, 2, False)
                    
                else:
                    self.metin_is_getting_killed = True
                    self.metins_rotation = 0
                    self.metins_killed += 1
                
                    self.metin_bot.stop(True, time.time()+5.5)
                
                return

            elif self.metins_rotation % 8 == 0:
                # self.metin_bot.osk_window.pull_mobs_different_version()
                # time.sleep(0.1)
                # self.metin_bot.osk_window.start_hitting()
                # time.sleep(0.1)
                # self.metin_bot.stop(True, time.time()+15.1)
                self.metin_bot.stop(True, time.time())
                return
            
        elif self.metins_rotation > self.max_metins_rotations and (self.metins_killed < (number_of_metins-1)):
                self.start_of_the_action_time = None
                self.restart_after_action_not_changed()

        else:

            # if enemy_after_kill and self.metin_have_been_killed:
            #     self.metin_bot.osk_window.start_hitting()
            #     time.sleep(0.09)
            #     self.metin_bot.osk_window.pull_mobs()
            #     time.sleep(0.15)
            #     self.metin_bot.osk_window.pull_mobs_different_version()
            #     time.sleep(0.04)
            #     self.metin_have_been_killed = False
            #     self.metin_bot.stop(True, time.time()+7)
            #     return
            
            self.metin_bot.osk_window.stop_hitting()
            self.metins_killed = 0
            self.metins_rotation = 0
            self.metin_have_been_killed = False
            self.metin_start_hitting_time = None
            self.start_of_the_action_time = None
            self.metin_bot.increment_state(False)

        # code to use a skill
    

    def kill_mini_boss(self, time_to_kill):
        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
            self.metin_bot.osk_window.start_hitting()
            time.sleep(0.1)
            self.metin_bot.osk_window.pull_mobs()
            time.sleep(0.15)
            self.picture_for_comparison = self.metin_bot.get_screenshot_info()
            self.metin_bot.osk_window.pull_mobs_different_version()
            time.sleep(0.04)
            self.metin_bot.stop(True, time.time()+6)
            return 
        self.metin_bot.osk_window.start_hitting()
        time.sleep(0.1)
        
        if time.time() - self.start_of_the_action_time > time_to_kill:
            time.sleep(0.1)
            # code to attack the monster
            self.start_of_the_action_time = None
            self.metin_bot.increment_state(True, time.time()+3)

        elif time.time() - self.start_of_the_action_time > time_to_kill-5:

           
            ## WE DONT KNOW IF HE DIDN'T KILL THE MONSTERS ALREADY AND IT TPED HIM TO NEXT STAGE WE CANT USE PULL MOBS IN NEXT STAGE
            time.sleep(0.04)
            picture_for_comparison2 = self.metin_bot.get_screenshot_info()
            pixels_difference_percentage = self.metin_bot.vision.compare_screenshots_percentage(self.picture_for_comparison, picture_for_comparison2)
            time.sleep(0.2)
            picture_for_comparison3 = self.metin_bot.get_screenshot_info()
            pixels_difference_percentage2 = self.metin_bot.vision.compare_screenshots_percentage(self.picture_for_comparison, picture_for_comparison3)
            logging.debug("pixels diff" + str(pixels_difference_percentage))
            logging.debug("pixels diff" + str(pixels_difference_percentage2))
            if pixels_difference_percentage >= 78 and pixels_difference_percentage2 >= 78:
                self.start_of_the_action_time = None
                self.metin_bot.increment_state(False)
                return
            
            time.sleep(0.12)
            self.metin_bot.stop(True, time.time()+6)

        else:
            self.metin_bot.stop(True, time.time()+5)

    
    def kill_metin(self):

        
        first_assumption = self.metins_rotation <= (self.max_metins_rotations - 10)
        second_assumption = self.metin_bot.get_top_center_position('metin', 0.1) is not None

        if first_assumption or second_assumption:
            time.sleep(0.1)
            is_clicked = self.metin_bot.detect_and_click('metin', metin_acc=0.45)
            self.metins_rotation += 1
            if is_clicked:
                self.start_of_the_action_time = None
                self.metin_bot.osk_window.activate_horse_dodge()
                self.metins_rotation = 0
                time.sleep(9)
                self.metin_bot.osk_window.start_hitting()
                time.sleep(0.09)
                self.metin_bot.osk_window.pull_mobs()
                time.sleep(0.15)
                self.metin_bot.osk_window.pull_mobs_different_version()
                time.sleep(0.04)
                self.metin_have_been_killed = False
                self.metin_bot.stop(True, time.time()+7)
                return True

        elif not first_assumption:
            self.start_of_the_action_time = None
            self.restart_after_action_not_changed()
            return True

    def click_items(self, image_of_item):
        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
            time.sleep(0.1)
            self.metin_bot.game_actions.open_inventory()
            time.sleep(0.7)

        if self.items_gathered < 4:
            centers = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), image_of_item, 0.6, 4)
            centers = sorted(centers, key=lambda center: center[1])
            index_of_next_click = self.metin_bot.vision.index_of_centers_that_hasnt_been_clicked_yet(centers, self.gather_items_stones_click, self.inventory_page)
            if centers is None or len(centers) == 0 or index_of_next_click is None:
                self.metin_bot.osk_window.pull_mobs()
                self.inventory_page = (self.inventory_page % 4) + 1
                self.metin_bot.game_actions.click_inventory_stash_x(self.inventory_page)
               
                ## SLEEP OR STOP 
                time.sleep(0.3)
                self.gather_items_stones_click = []
               
                if self.inventory_page == 1:
                    kill_metins_time = time.time() + 5
                    while not self.kill_metin() and time.time() < kill_metins_time:
                        time.sleep(0.001)
                    self.start_of_the_action_time = None
                    
                    return
                
            else:
                for count, value in enumerate(centers):
                    if count != 0: 
                        index_of_next_click = self.metin_bot.vision.index_of_centers_that_hasnt_been_clicked_yet(centers, self.gather_items_stones_click, self.inventory_page)
                    else:
                        self.last_inventory_page_used = self.inventory_page
                    if index_of_next_click is not None:
                        self.metin_bot.metin_window.mouse_move(centers[index_of_next_click][0],centers[index_of_next_click][1])
                        time.sleep(0.05)
                        self.metin_bot.metin_window.mouse_right_click()
                        time.sleep(0.03)
                        self.gather_items_stones_click.append([centers[index_of_next_click][0], centers[index_of_next_click][1], self.inventory_page])
                        self.items_gathered += 1
                

        if self.items_gathered > 3:
            self.metin_bot.game_actions.click_inventory_stash_x(self.last_inventory_page_used)
            self.inventory_page = self.last_inventory_page_used
            time.sleep(0.1)
            self.metin_bot.game_actions.close_inventory() #close inventory
            self.start_of_the_action_time = None
            #self.metin_bot.game_actions.turn_on_buffs()
            #time.sleep(0.1)
            self.metin_bot.increment_state(True, time.time()+3)


    def end_boss(self, time_to_kill=25):
        
        x, y = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_dangeon_end_image(), 0.9)
        if x is not None:
            self.start_of_the_action_time = time.time() - 100
        else:
            self.metin_bot.osk_window.start_hitting()
            time.sleep(0.03)
            self.metin_bot.osk_window.pull_mobs()
            time.sleep(0.12)
            if self.start_of_the_action_time is None:
                self.start_of_the_action_time = time.time()
                self.metin_bot.game_actions.turn_on_buffs()
                #self.metin_bot.game_actions.calibrate_view("first_arena_middlepoint")


        if self.start_of_the_action_time + time_to_kill <= time.time():
            self.metin_bot.osk_window.stop_hitting()
            self.start_of_the_action_time = None

            self.stats.log_statistics()

            #self.metin_bot.game_actions.collect_the_event_card_drop()

            x, y = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_dangeon_end_image(), 0.9)
            if x is None:
                 self.tp_to_dangeon = True
                 self.change_channel = True
                 self.restart_after_action_not_changed()
            else:
                self.metin_bot.dangeon_end_time = time.time()
                self.metin_bot.dangeons_count += 1
                self.stats.add_dungeon_completed(self.metin_bot.dangeon_end_time - self.metin_bot.dangeon_entered_time)
                self.restart_class_props(False)
                self.metin_bot.increment_state(True, time.time()+3)
            
        else:
            self.metin_bot.stop(True, time.time()+12)


    def debug(self):
        # code to loot items
        pass

    def restart_class_props(self, bug=True):
        self.metins_killed = 0
        self.gather_items_time = 102
        self.items_gathered = 0
        #self.inventory_page = 2
        self.arena_middlepoint = False
        self.start_of_the_action_time = None
        self.metin_start_hitting_time = None
        self.metin_is_getting_killed = False
        self.metin_have_been_killed = False
        self.metins_rotation = 0
        self.pick_up_stop = False
        self.guard_clicked = False
        self.gather_items_stones_click = []
        if bug:
            print("ACTION RESTARTED WITH BUG IN {}".format(self.metin_bot.state.name))
            self.stats.add_bug_encountered()

        # if 

        self.metin_bot.game_actions.close_inventory()


    def restart_after_action_not_changed(self):
        self.restart_class_props()
        logging.debug("ACTION RESTARTED WITH BUG IN {}".format(self.metin_bot.state.name))
        self.tp_to_dangeon = True
        self.change_channel = True
        self.metin_bot.health_checks_bool = True
        self.metin_bot.switch_state(DangeonState.INITIALIZING)
