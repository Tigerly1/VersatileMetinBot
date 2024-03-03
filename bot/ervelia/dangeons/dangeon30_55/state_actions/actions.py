import enum
import random
import time
from typing import TYPE_CHECKING
from bot.ervelia.dangeons.dangeon30_55.state import DangeonState
from bot.stats.dangeon import DungeonBotStatistics
if TYPE_CHECKING:
    from bot.core_loop import MetinBot  # This import is only for type checking
from utils.helpers.paths import get_dangeon_end_image, get_dangeon_item_dangeon30, get_first_area_dangeon30, get_second_area_dangeon30

import logging

# Configure logging
logging.basicConfig(filename="debug", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


LABELS = ['metin', 'boss', 'guard', 'first_arena', 'second_arena']

class Actions:
    def __init__(self, metin_bot: 'MetinBot'):
        self.metin_bot = metin_bot


        ### states to clear
        self.first_metins_killed = 0
        self.picture_for_comparison = None
        self.gather_items_time = 102
        self.last_inventory_page_used = 2
        self.gather_items_stones_click = []
        self.items_gathered = 0
        self.inventory_page = 1
        self.second_metins_killed = 0
        self.detect_boss_tries = 5
        self.tp_to_dangeon = False ######## if you are already in dang
        self.change_channel = False
        self.start_of_the_action_time = None
        self.metin_start_hitting_time = None
        self.pick_up_stop = False
        self.metins_rotation = 0
        self.guard_clicked = True ######## if you are already in dang
        self.metin_is_getting_killed = False
        self.metin_click_delayed = False
        self.metin_have_been_killed = False
        self.max_metins_rotations = 14
        self.min_metins_rotations = 6
        self.inventory_pages_clicked = 0
        self.first_arena_key_holded = False
        self.metins_killed = 0

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
                    self.metin_bot.game_actions.calibrate_view_dang30("guard")
                    self.start_of_the_action_time = None
                    #self.metin_bot.stop()
                    return
                if random.random() < 0.01:
                    self.tp_to_dangeon = True
                    self.start_of_the_action_time = None
                    self.metin_bot.health_checks_bool = True
                    self.metin_bot.stop()
                    return
                
                if random.random() < 0.01:
                   if self.metin_bot.game_actions.check_if_you_cannot_tp_to_dangeon():
                        self.start_of_the_action_time = None
                        self.metin_bot.stop()

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
    


    def first_arena(self):
        if self.start_of_the_action_time is None:
            if self.metin_bot.game_actions.check_if_you_cannot_tp_to_dangeon():
                self.start_of_the_action_time = None
                self.restart_after_action_not_changed()
                return
            self.start_of_the_action_time = time.time()

        if time.time() - self.start_of_the_action_time > 90:
            self.start_of_the_action_time = None
            self.restart_after_action_not_changed()
            return

        if time.time() - self.start_of_the_action_time > 40:
            self.metin_bot.game_actions.calibrate_view_dang30('first_arena')

        self.rotate_start_time = time.time()

        while time.time() - self.rotate_start_time  < 1.5:
            result = self.metin_bot.brief_detection('first_arena', detection_acc=0.61)
            if result:
                break
        
        if not result:
            self.metin_bot.stop(True, time.time())
            return
        new_click = False
        if result:
            for x in range(0, 5):
                time.sleep(0.06)
                new_click = self.metin_bot.detect_and_click('first_arena', rotate_before_click=True, small_rotation=True, detection_acc=0.61)
                if new_click:
                    break
            if not new_click:
                self.metin_bot.stop(True, time.time())
                return
        if not result:    
            self.metin_bot.stop(True, time.time())
            return
        if new_click:
            
            self.start_of_the_action_time = None
            self.metin_bot.increment_state(True, time.time()+5)

    def kill_mobs(self):
        
        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
            time.sleep(0.1)
            self.metin_bot.osk_window.start_hitting()
            time.sleep(0.09)
            self.metin_bot.osk_window.pull_mobs()
            time.sleep(0.15)
            self.metin_bot.osk_window.pull_mobs_different_version()
            time.sleep(0.04)
            self.metin_bot.stop(True, time.time()+11)
            return
        
        if time.time() - self.start_of_the_action_time > 11:   
            self.metin_bot.osk_window.stop_hitting()
            self.start_of_the_action_time = None
            self.metin_bot.increment_state(False)
        else:
            self.metin_bot.stop()
    
    # def kill_metins(self):
    #     if self.start_of_the_action_time is None:
    #         self.start_of_the_action_time = time.time()
    #         time.sleep(0.05)
    #         self.metin_bot.game_actions.turn_on_buffs()
    #         time.sleep(0.1)
        
    #     first_assumption = self.first_metins_killed < 4  and self.metins_rotation <= self.max_metins_rotations
    #     second_assumption = self.metin_bot.detection_result is not None and self.metin_bot.detection_result['labels'][0] == LABELS[0]

    #     if self.first_metins_killed > 0:
    #         self.metin_bot.moving_to_enemy()

    #     if self.first_metins_killed > 3 and not second_assumption:
    #         self.metin_bot.osk_window.rotate_with_mouse(False,True)
    #         time.sleep(0.12)

    #     if first_assumption or second_assumption:
    #         if second_assumption and not first_assumption:
    #              self.metin_bot.osk_window.activate_flag()
    #         time.sleep(0.1)
    #         is_clicked = self.metin_bot.detect_and_click('metin')
    #         self.metins_rotation += 1
    #         if is_clicked:
    #             if self.first_metins_killed == 0:
    #                 self.metin_bot.osk_window.activate_flag()
    #                 time.sleep(0.1)

    #             self.metins_rotation = 0
    #             self.first_metins_killed += 1
    #             self.metin_bot.stop(True, time.time()+6)
                
    #             return

    #         elif self.metins_rotation % 12 == 0:
    #             self.metin_bot.osk_window.pull_mobs_different_version()
    #             self.metin_bot.osk_window.start_hitting()
    #             self.metin_bot.stop(True, time.time()+15.1)
    #             return
            
    #     elif self.metins_rotation > self.max_metins_rotations:
           
            
    #         self.start_of_the_action_time = None
    #         self.restart_after_action_not_changed()

    #     else:
    #         self.metins_rotation = 0
    #         self.metin_start_hitting_time = None
    #         self.start_of_the_action_time = None
    #         self.metin_bot.increment_state(False)

        # code to use a skill
    
    def kill_mini_boss(self):
        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
            self.metin_bot.osk_window.start_hitting()
            time.sleep(0.1)
            self.metin_bot.osk_window.pull_mobs()
            time.sleep(0.15)
            self.picture_for_comparison = self.metin_bot.get_screenshot_info()
            self.metin_bot.osk_window.pull_mobs_different_version()
            time.sleep(0.04)
            self.metin_bot.stop(True, time.time()+12)
            return 
        self.metin_bot.osk_window.start_hitting()
        time.sleep(0.1)
        
        if time.time() - self.start_of_the_action_time > 26:
            time.sleep(0.1)
            # code to attack the monster
            self.start_of_the_action_time = None
            self.metin_bot.increment_state(True, time.time()+3)

        elif time.time() - self.start_of_the_action_time > 16:

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
                self.metin_bot.increment_state(True)
                return
            
            self.metin_bot.osk_window.pull_mobs()
            time.sleep(0.12)
            self.metin_bot.stop(True, time.time()+6)

        else:
            self.metin_bot.stop(True, time.time()+5)

        

    def second_arena(self):

        self.metin_bot.osk_window.stop_hitting()
        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()

        if time.time() - self.start_of_the_action_time > 45:
            self.metin_bot.game_actions.calibrate_view_dang30('second_arena')
            
        if time.time() - self.start_of_the_action_time > 90:
            self.restart_after_action_not_changed()
            return
        
        self.rotate_start_time = time.time()

        while time.time() - self.rotate_start_time  < 1:
            result = self.metin_bot.brief_detection('second_arena',  detection_acc=0.6)
            if result:
                break
        if not result:
            self.metin_bot.stop(True, time.time())
            return
        
        self.metin_bot.osk_window.activate_flag()
        time.sleep(0.02)
        new_click = self.metin_bot.detect_and_click('second_arena',  detection_acc=0.6)

        if not new_click:
            self.metin_bot.stop(True, time.time()+6)
            return
            

        self.start_of_the_action_time = None
        self.metin_bot.increment_state(True, time.time()+5)
        # code to move to the next room

    def gather_items(self):
        if self.start_of_the_action_time is None:
            self.metin_bot.osk_window.start_hitting()
            self.start_of_the_action_time = time.time()
            time.sleep(0.1)
            self.metin_bot.game_actions.open_inventory()

        self.metin_bot.osk_window.start_hitting()

        if self.items_gathered <= 0:
            time.sleep(0.03)
            self.metin_bot.osk_window.pull_mobs()
            time.sleep(0.09)
        if time.time() - self.start_of_the_action_time < self.gather_items_time - 12:
            self.metin_bot.stop(True, time.time()+12)
            return
        elif time.time() - self.start_of_the_action_time < self.gather_items_time:
            self.metin_bot.stop(True, time.time() + abs(time.time() - self.start_of_the_action_time -  self.gather_items_time))
            return
        elif time.time() - self.start_of_the_action_time > 200:
            self.start_of_the_action_time = None
            self.restart_after_action_not_changed()
            return

        if self.items_gathered < 4:
            centers = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_dangeon_item_dangeon30(), 0.6, 4)
            centers = sorted(centers, key=lambda center: center[1])
            index_of_next_click = self.metin_bot.vision.index_of_centers_that_hasnt_been_clicked_yet(centers, self.gather_items_stones_click, self.inventory_page)
            if centers is None or len(centers) == 0 or index_of_next_click is None:
                self.metin_bot.osk_window.pull_mobs()
                self.inventory_page = (self.inventory_page % 4) + 1
                self.metin_bot.game_actions.click_inventory_stash_x(self.inventory_page)
               
                
                time.sleep(0.03)
                self.gather_items_stones_click = []
               
                if self.inventory_page == 1:
                    self.metin_bot.stop(True, time.time()+15)
                    return
                else:
                     self.metin_bot.stop(True, time.time())
            else:
                for count, value in enumerate(centers):
                    if count != 0: 
                        index_of_next_click = self.metin_bot.vision.index_of_centers_that_hasnt_been_clicked_yet(centers, self.gather_items_stones_click, self.inventory_page)
                    else:
                        self.last_inventory_page_used = self.inventory_page
                    if index_of_next_click is not None:
                        if self.items_gathered == 3:
                            self.metin_bot.osk_window.stop_hitting()
                        self.metin_bot.metin_window.mouse_move(centers[index_of_next_click][0],centers[index_of_next_click][1])
                        time.sleep(0.05)
                        self.metin_bot.metin_window.mouse_right_click()
                        time.sleep(0.03)
                        self.gather_items_stones_click.append([centers[index_of_next_click][0], centers[index_of_next_click][1], self.inventory_page])
                        self.items_gathered += 1
                

        if self.items_gathered > 3:
            self.metin_bot.osk_window.stop_hitting()
            self.metin_bot.game_actions.click_inventory_stash_x(self.last_inventory_page_used)
            self.inventory_page = self.last_inventory_page_used
            time.sleep(0.1)
            self.metin_bot.game_actions.close_inventory() #close inventory
            self.start_of_the_action_time = None
            time.sleep(0.1)
            self.metin_bot.increment_state(False)

    def kill_metins(self, number_of_metins, enemy_after_kill=False, detection_acc = 0.52, random_choice=False):

        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
            time.sleep(0.05)
            self.metin_bot.game_actions.turn_on_buffs(only_potions=True)
            time.sleep(0.1)


        if enemy_after_kill and self.metin_have_been_killed:
            self.metin_bot.osk_window.start_hitting()
            time.sleep(0.06)
            # self.metin_bot.osk_window.pull_mobs()
            # time.sleep(0.15)
            self.metin_have_been_killed = False
            self.metin_bot.stop(True, time.time()+3.2)
            return
        
        
        if self.metin_bot.moving_to_enemy_flag_clicked or enemy_after_kill:
            self.metin_bot.osk_window.stop_hitting()


        if self.metin_click_delayed:
            self.metin_click_delayed = False
            #self.metins_killed += 1
            self.metin_bot.stop(True, time.time()+8)
            return
       
        look_for_less_metins = 1 if enemy_after_kill else 0
        
        first_assumption = (self.metins_killed < (number_of_metins-look_for_less_metins)  and self.metins_rotation <= self.max_metins_rotations)
        second_assumption = self.metin_bot.get_top_center_position('metin', 0.5) is not None and self.metins_killed < 2 * number_of_metins
        third_assumption = self.min_metins_rotations >= self.metins_rotation

        # check_match = True if enemy_after_kill and not random_choice else False
        check_match = True
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
                self.metin_bot.stop(True, time.time()+4)
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
                self.metin_bot.osk_window.rotate_with_mouse(False,False)
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

                        ### turn it on if more accounts are used
                        #self.metin_have_been_killed = True
                        #self.metin_bot.stop(True, time.time()+6.0, 2, False)
                        self.metin_is_getting_killed = True
                        self.metin_bot.stop(True, time.time()+3.5)
                    
                else:
                    self.metin_is_getting_killed = True
                    self.metins_rotation = 0
                    self.metins_killed += 1
                
                    self.metin_bot.stop(True, time.time()+3)
                
                return

            elif self.metins_rotation % 4 == 0:
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

    def second_metins(self):
        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()

        first_assumption = self.second_metins_killed < 4  and self.metins_rotation <= self.max_metins_rotations
        second_assumption = self.metin_bot.detection_result is not None and self.metin_bot.detection_result['labels'][0] == LABELS[0]

        if self.second_metins_killed > 0:
            self.metin_bot.moving_to_enemy()

        if self.second_metins_killed > 3 and not second_assumption:
            self.metin_bot.osk_window.rotate_with_mouse(False,True)
            time.sleep(0.12)
            self.metin_bot.detect_and_click('metin')

        if first_assumption or second_assumption:
            if second_assumption and not first_assumption:
                 self.metin_bot.osk_window.activate_flag()
            time.sleep(0.1)
            is_clicked = self.metin_bot.detect_and_click('metin')
            self.metins_rotation += 1
            if is_clicked:
                self.metin_start_hitting_time = time.time()
                self.metins_rotation = 0
                if self.second_metins_killed == 0:
                    self.metin_bot.osk_window.activate_flag()
                    time.sleep(0.1)
                #time.sleep(5)
                self.metin_bot.stop(True, time.time()+6)
                self.second_metins_killed += 1
                return
            elif self.metins_rotation % 12 == 0:
                self.metin_bot.stop(True, time.time()+14.1)
                return
            
        elif self.metins_rotation > self.max_metins_rotations:
            self.start_of_the_action_time = None
            self.restart_after_action_not_changed()
        else:
        # if self.second_metins_killed  >= 4 or self.metins_rotation > self.max_metins_rotations:
            self.metins_rotation = 0
            self.metin_start_hitting_time = None
            self.start_of_the_action_time = None
            self.metin_bot.increment_state(False)

    def second_mini_boss(self):
       
        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
            self.metin_bot.osk_window.start_hitting()
            time.sleep(0.2)
            # self.metin_bot.game_actions.turn_on_buffs()
            # time.sleep(0.4)
            self.metin_bot.osk_window.pull_mobs()
            time.sleep(0.08)
            self.metin_bot.stop(True, time.time()+8)
            return
        
        self.metin_bot.osk_window.start_hitting()
        time.sleep(0.03)
        self.metin_bot.osk_window.pull_mobs()
        time.sleep(0.1)

        if self.start_of_the_action_time + 15 <= time.time() and (self.metin_bot.detection_result is not None and "boss" in self.metin_bot.detection_result['labels']):
            self.start_of_the_action_time = None
            time.sleep(0.1)
            self.metin_bot.increment_state(False)
        # BOS ZNIKL Z PLANETY ZIEMIA W TYM MIEJSCU
 
        elif self.start_of_the_action_time + 32 <= time.time():
            self.start_of_the_action_time = None
            time.sleep(0.1)
            self.metin_bot.increment_state(False)

        else:
            x, y = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_dangeon_end_image(), 0.9)
            if x is not None:
                self.metin_bot.increment_state(False)
            top_left = (300, 21)
            bottom_right = (700, 60)
            mob_text = self.metin_bot.game_actions.get_clicked_place_info(top_left, bottom_right)
            if "Prymus Myrow" in mob_text:
                 self.start_of_the_action_time = None
                 self.metin_bot.increment_state(False)
            else:

                self.metin_bot.stop(True, time.time()+2)
        # code to attack the monster

    def end_boss(self):
        
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
                self.metin_bot.game_actions.turn_on_buffs(only_potions=True)

        if self.start_of_the_action_time + 76 <= time.time():
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
                self.metin_bot.increment_state(False)

            
        else:
            self.metin_bot.stop()


    def debug(self):
        # code to loot items
        pass

    def restart_class_props(self, bug=True):
        self.first_metins_killed = 0
        self.gather_items_time = 110
        self.items_gathered = 0
        #self.inventory_page = 2
        self.second_metins_killed = 0
        self.start_of_the_action_time = None
        self.metin_start_hitting_time = None
        self.metin_is_getting_killed = False
        self.metin_have_been_killed = False
        self.metins_rotation = 0
        self.inventory_pages_clicked = 0
        self.pick_up_stop = False
        self.guard_clicked = False
        self.first_arena_key_holded = False
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
