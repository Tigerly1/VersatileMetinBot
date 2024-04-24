import random
import time

from typing import TYPE_CHECKING
from bot.ervelia.dangeons.elephant_dangeon.state import DangeonState
from bot.ervelia.dangeons.elephant_dangeon.state_actions.actions import Actions

from bot.interfaces.dungeon_strategy_interface import DangeonStateStrategy
from utils.helpers.paths import ERVELIA_DANG75_IMAGE_PATHS
if TYPE_CHECKING:
    from bot.core_loop import MetinBot  # This import is only for type checking

class ElephantDangeonStateOrder(DangeonStateStrategy):
    # def __init__(self):
    #    self.dangeon_actions = Actions(self)

    def init_actions_passing_variables(self, context: "MetinBot"):
        self.dangeon_actions = Actions(context)

    def get_first_state(self):
        return DangeonState.ENTER_THE_DANGEON
    
    def get_last_state_from_iteration(self):
        return DangeonState.END_BOSS
    
    def get_next_state(self, state:DangeonState):
        return DangeonState(state.value + 1)

    def get_logging_state(self):
        return DangeonState.LOGGING

    def get_initializing_state(self):
        return DangeonState.INITIALIZING
    
    def detect_and_click_custom_workflow_before_click(self, context: "MetinBot", label, x, y, saved_click_pos): 
        if label == "statue":
            if  x > 700:
                context.game_actions.rotate_view(small_rotation=True)
                self.time_of_new_screen = time.time()
                return False, False
            elif x < 80:
                context.game_actions.rotate_view(small_rotation=True, rotate_right=True)
                context.time_of_new_screen = time.time()
                return False, False
            y = y + 55
            context.metin_window.mouse_move(x,y)
        return x, y
    
    def execute_actions_by_state(self, context: "MetinBot"):
        time.sleep(0.002)
        while not context.stopped:

            ## DO THE HEALTH CHECKS IN SEPERATE THREAD ALSO TO NOT BLOCK THE CLICKING
            
            if context.is_calibrating:
                context.game_actions.calibrate_view()
                continue

            context.health_checks_iterations = (context.health_checks_iterations + 1) % 40
            ## check if dead every 10 iterations and if dead then fight back iterate
            if context.does_it_need_newest_window_detections_after_swap and context.health_checks_iterations % 20 == 0:
                if context.last_turn_alchemy_time + 23*60*60 < time.time():
                    context.game_actions.renew_alchemy()
                    context.last_turn_alchemy_time = time.time()

                if context.game_actions.respawn_if_dead():
                    time.sleep(0.1)
                    context.osk_window.start_hitting()
                    time.sleep(0.09)
                    context.osk_window.pull_mobs()
                    time.sleep(0.15)
                    context.stop(True, time.time() + 6, 0)
                continue

            if context.health_checks_iterations == 35 or context.health_checks_bool:
                context.health_checks_bool = False
                context.game_actions.health_checks(700)
                continue 
            
            if context.state == DangeonState.INITIALIZING:
                context.metin_window.activate()
                #context.game_actions.calibrate_view("guard")
                context.game_actions.get_the_player_on_the_horse()
                context.game_actions.zoom_out()
                #context.game_actions.remove_dangon_items_from_inv()
                context.switch_state(DangeonState.ENTER_THE_DANGEON)
                continue

            if context.state == DangeonState.DEBUG:
                # context.osk_window.start_hitting()
                # time.sleep(0.1)
                # context.osk_window.pull_mobs()
                # time.sleep(0.1)
                # context.osk_window.start_pick_up()
                # time.sleep(1)
                # context.osk_window.end_pick_up()
                context.osk_window.mouse_move(690,65)
                time.sleep(0.1)
                for i in range(0, 1000):
                    context.osk_window.mouse_right_click()
                    time.sleep(random.randint(10)/100)
                # time.sleep(2)
                # context.game_actions.turn_on_buffs(True)
                # time.sleep(0.1)
                # context.osk_window.mouse_move(690,93)
                # time.sleep(5)
                # context.game_actions.calibrate_view("first_arena_middlepoint")
                # context.osk_window.rotate_with_mouse(True, False, False)
                # context.osk_window.rotate_with_mouse(False, True, False)
                # context.osk_window.rotate_with_mouse(False, False, True)
                # context.game_actions.check_if_player_is_logged_out()
                # context.game_actions.remove_dangon_items_from_inv(images_path=ERVELIA_DANG75_IMAGE_PATHS)
                # context.game_actions.renew_alchemy()
                #context.game_actions.change_channel(context.current_channel)

                time.sleep(12)
                context.switch_state(DangeonState.DEBUG)
                continue
                
            if context.state == DangeonState.LOGGING:
                context.game_actions.check_if_player_is_logged_out()
                time.sleep(0.1)
                continue

            if context.state == DangeonState.ENTER_THE_DANGEON:
                self.dangeon_actions.enter_the_dangeon()
                continue

            if context.state == DangeonState.KILL_METINS:
                self.dangeon_actions.kill_metins(4)
                continue

            if context.state == DangeonState.KILL_MOBS:
                self.dangeon_actions.kill_mobs(165, 3)
                continue

            if context.state == DangeonState.KILL_SECOND_METINS:
                self.dangeon_actions.kill_metins(10)
                continue

            if context.state == DangeonState.KILL_SECOND_MOBS:
                self.dangeon_actions.kill_mobs(39)
                continue

            if context.state == DangeonState.KILL_MINIBOSS:
                self.dangeon_actions.kill_mini_boss(12)
                continue

            if context.state == DangeonState.KILL_STATUE:
                self.dangeon_actions.kill_statue(110)
                continue

            if context.state == DangeonState.KILL_THIRD_MOBS:
                self.dangeon_actions.kill_mobs(19, 4, True, True)
                continue

            if context.state == DangeonState.KILL_THIRD_METINS:
                self.dangeon_actions.kill_metins(8)
                continue
            
            if context.state == DangeonState.END_BOSS:
                self.dangeon_actions.end_boss(110)
                continue