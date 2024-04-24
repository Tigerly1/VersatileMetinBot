import enum
import random
import time
from typing import TYPE_CHECKING
from bot.ervelia.dangeons.elephant_dangeon.state import DangeonState
from bot.stats.dangeon import DungeonBotStatistics
if TYPE_CHECKING:
    from bot.core_loop import MetinBot  # This import is only for type checking
from utils.helpers.paths import get_dangeon_end_image, get_dangeon_item_dangeon30, get_dangeon_start_action_wtih_time_image, get_first_area_dangeon30, get_second_area_dangeon30

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
        self.max_metins_rotations = 14
        self.min_metins_rotations = 5
        self.inventory_pages_clicked = 0
        self.statue_clicked = False
        self.metins_rotation = 0
        self.guard_clicked = False
        self.first_arena_key_holded = False

        self.stats = DungeonBotStatistics()

    def enter_the_dangeon(self):
        self.metin_bot.game_actions.turn_on_buffs()
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
    

    def kill_mobs(self, time_to_kill=11, time_of_pull_stop=5, increment_state=True, turn_on_timer=False):
        if self.start_of_the_action_time is None:
            if turn_on_timer:
                self.metin_bot.game_actions.tp_to_dangeon_again()


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
        self.metin_bot.osk_window.start_pick_up()
        time.sleep(0.2)
        self.metin_bot.osk_window.end_pick_up()

        if time.time() - self.start_of_the_action_time > time_to_kill:   
            self.metin_bot.osk_window.stop_hitting()
            self.start_of_the_action_time = None
            if increment_state:
                self.metin_bot.increment_state(False)
            else:
                self.metin_bot.stop()
        else:
            if time.time() - self.start_of_the_action_time > time_to_kill-9:
                 self.metin_bot.stop(True, time_to_kill + self.start_of_the_action_time , newest_detection_needed=False)
            else:
                self.metin_bot.stop(True, time.time()+8, newest_detection_needed=False)
    
    def kill_metins(self, number_of_metins, enemy_after_kill=False, detection_acc = 0.67, random_choice=False, check_match=False):

        if self.start_of_the_action_time is None:
            self.start_of_the_action_time = time.time()
            time.sleep(0.05)
            

        # if number_of_metins == 4 and self.metins_killed == 2:
        #     enemy_after_kill = True


        if enemy_after_kill and self.metin_have_been_killed:
            self.metin_bot.osk_window.start_hitting()
            time.sleep(0.06)
            # self.metin_bot.osk_window.pull_mobs()
            # time.sleep(0.15)
            self.metin_have_been_killed = False
            self.metin_bot.stop(True, time.time()+8.5)
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

        #check_match = True if enemy_after_kill and not random_choice else False

        #if self.metins_killed > 0:
        if self.metin_is_getting_killed:

            #self.metin_bot.osk_window.start_hitting()
            if not self.metin_bot.moving_to_enemy(hitting_time=6):
                self.metin_is_getting_killed = False
                self.metin_have_been_killed = True
                return
            
            else:
                ## metin will be probably killed there
                self.metins_killed += 1
                self.metin_click_delayed = True
                self.metin_bot.stop(True, time.time()+7)
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
                
                self.metin_bot.game_actions.turn_on_buffs()
                # if enemy_after_kill:
                #     time.sleep(0.2)
                #     self.metin_bot.osk_window.activate_horse_dodge()
                # if self.metins_killed < 2:
                #     time.sleep(0.2)
                    #self.metin_bot.osk_window.activate_horse_dodge()
                if number_of_metins == 4 and self.metins_killed > 0:
                    self.metin_bot.osk_window.activate_flag()

                elif number_of_metins == 10 and self.metins_killed == 0:
                    self.metin_bot.osk_window.activate_flag()

                if enemy_after_kill:
                    # if self.metin_bot.game_actions.is_player_hitting_enemy():
                        #self.metin_bot.osk_window.start_hitting()
                        self.metins_rotation = 0
                        self.metins_killed += 1

                        ### turn it on if more accounts are used
                        #self.metin_have_been_killed = True
                        #self.metin_bot.stop(True, time.time()+6.0, 2, False)
                        self.metin_is_getting_killed = True
                        self.metin_bot.stop(True, time.time()+4.5)
                    
                else:
                    self.metin_is_getting_killed = True
                    self.metins_rotation = 0
                    self.metins_killed += 1
                
                    self.metin_bot.stop(True, time.time()+4.5)
                
                return

            elif self.metins_rotation % 8 == 0:
                self.metin_bot.stop(True, time.time())
                return
            
        elif self.metins_rotation > self.max_metins_rotations and (self.metins_killed < (number_of_metins-1)):
                self.start_of_the_action_time = None
                self.restart_after_action_not_changed()

        else:
            
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
            self.metin_bot.game_actions.turn_on_buffs()

            self.metin_bot.stop(True, time.time()+6)
            return 
        self.metin_bot.osk_window.start_hitting()
        time.sleep(0.1)
        
        if time.time() - self.start_of_the_action_time > time_to_kill:
            time.sleep(0.1)
            self.metin_bot.osk_window.stop_hitting()
            # code to attack the monster
            self.start_of_the_action_time = None
            self.metin_bot.increment_state(False)

        elif time.time() - self.start_of_the_action_time > time_to_kill-8:

            if  self.metin_bot.get_top_center_position('statue', 0.7) is not None:
                time.sleep(0.1)
                self.metin_bot.osk_window.stop_hitting()
            
                self.start_of_the_action_time = None
                self.metin_bot.increment_state(True, time.time()+1)
                return
            
            time.sleep(0.12)
            self.metin_bot.stop(True, time.time()+2)

        else:
            self.metin_bot.stop(True, time.time()+2)

    def kill_statue(self, time_to_kill):
        ## DETECT THE STATUE AND WAIT FOR 2 MINUTES TO KILL IT
        if not self.statue_clicked:
            if self.metins_rotation > 15:
                self.metins_rotation = 0
                self.metin_bot.switch_state(DangeonState.KILL_MINIBOSS)
                return

            time.sleep(0.07)
            self.statue_clicked = self.metin_bot.detect_and_click('statue')

            if not self.statue_clicked:
                self.metins_rotation += 1
                return
            
        self.metins_rotation = 0
        self.metin_bot.game_actions.turn_on_buffs()
        if self.start_of_the_action_time is None:
            time.sleep(1.5)
            self.start_of_the_action_time = time.time()
           
        time.sleep(0.07)
        x, y = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_dangeon_start_action_wtih_time_image(), 0.86)
        if x is not None:
            self.start_of_the_action_time = None
            self.metin_bot.increment_state(True, time.time())
            return 
        
        # if time.time() - self.start_of_the_action_time > time_to_kill:   
        #     self.start_of_the_action_time = None
        #     self.metin_bot.increment_state(True, time.time())
        if time.time() - self.start_of_the_action_time > time_to_kill:
            self.start_of_the_action_time = None
            self.statue_clicked = False
            self.metin_bot.switch_state(DangeonState.KILL_MINIBOSS)
            return

        else:
            if time.time() - self.start_of_the_action_time > time_to_kill-9:
                 self.metin_bot.stop(True, time_to_kill + self.start_of_the_action_time)
            else:
                self.metin_bot.stop(True, time.time()+1.5)


    def end_boss(self, time_to_kill=25):
        
        x, y = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_dangeon_end_image(), 0.9)
        if x is not None:
            self.start_of_the_action_time = time.time() - time_to_kill - 100
        else:
            self.metin_bot.osk_window.start_hitting()
            time.sleep(0.03)
            self.metin_bot.osk_window.pull_mobs()
            time.sleep(0.12)
            self.metin_bot.game_actions.turn_on_buffs()
            if self.start_of_the_action_time is None:
                self.start_of_the_action_time = time.time()
                #self.metin_bot.game_actions.turn_on_buffs()
            # else:
            #     self.metin_bot.game_actions.turn_on_buffs(True)
                #self.metin_bot.game_actions.calibrate_view("first_arena_middlepoint")


        if self.start_of_the_action_time + time_to_kill <= time.time():
            self.metin_bot.osk_window.stop_hitting()
            self.stats.log_statistics()

            #self.metin_bot.game_actions.collect_the_event_card_drop()

            x, y = self.metin_bot.vision.find_image(self.metin_bot.get_screenshot_info(), get_dangeon_end_image(), 0.9)
            if x is None: 
                 if self.start_of_the_action_time + time_to_kill <= time.time() and self.start_of_the_action_time + time_to_kill >= time.time() + 50:
                    if self.start_of_the_action_time + time_to_kill <= time.time() and self.start_of_the_action_time + time_to_kill >= time.time() + 12:
                        self.metin_bot.game_actions.get_the_player_on_the_horse()
                        self.metin_bot.health_checks_bool = True
                    self.metin_bot.stop(True, time.time()+12)


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
            self.metin_bot.stop(True, time.time()+3)


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
        self.statue_clicked = False
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
