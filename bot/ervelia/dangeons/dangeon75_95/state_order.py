import random
import time

from typing import TYPE_CHECKING
from bot.ervelia.dangeons.dangeon75_95.state import DangeonState
from bot.ervelia.dangeons.dangeon75_95.state_actions.actions import Actions

from bot.interfaces.dungeon_strategy_interface import DangeonStateStrategy
from utils.helpers.paths import ERVELIA_DANG75_IMAGE_PATHS
if TYPE_CHECKING:
    from bot.core_loop import MetinBot  # This import is only for type checking

class Dangeon75StateOrder(DangeonStateStrategy):
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
    
    def execute_actions_by_state(self, context: "MetinBot"):
        time.sleep(0.002)
        while not context.stopped:

            ## DO THE HEALTH CHECKS IN SEPERATE THREAD ALSO TO NOT BLOCK THE CLICKING
            context.health_checks_iterations = (context.health_checks_iterations + 1) % 50

            ## check if dead every 10 iterations and if dead then fight back iterate
            if context.does_it_need_newest_window_detections_after_swap and context.health_checks_iterations % 20 == 0:
                if context.game_actions.respawn_if_dead():
                    time.sleep(0.1)
                    context.osk_window.start_hitting()
                    time.sleep(0.09)
                    context.osk_window.pull_mobs()
                    time.sleep(0.15)
                continue

            if context.health_checks_iterations == 45 or context.health_checks_bool:
                context.game_actions.health_checks(960)
                context.health_checks_bool = False
                continue 
            
            if context.state == DangeonState.INITIALIZING:
                context.metin_window.activate()
                context.game_actions.calibrate_view("guard")
                context.game_actions.get_the_player_on_the_horse()
                context.game_actions.zoom_out()
                #context.game_actions.remove_dangon_items_from_inv()
                context.switch_state(DangeonState.ENTER_THE_DANGEON)
                continue

            if context.state == DangeonState.DEBUG:

                # context.osk_window.mouse_move(690,93)
                # time.sleep(5)
                context.switch_state(DangeonState.DEBUG)
                continue
                
            if context.state == DangeonState.LOGGING:
                context.game_actions.check_if_player_is_logged_out()
                time.sleep(0.1)
                continue

            if context.state == DangeonState.ENTER_THE_DANGEON:
                self.dangeon_actions.enter_the_dangeon()
                continue

            if context.state == DangeonState.FIRST_ARENA:
                self.dangeon_actions.enter_arena("first_arena")
                continue

            if context.state == DangeonState.KILL_MOBS:
                self.dangeon_actions.kill_mobs(88)
                continue

            if context.state == DangeonState.KILL_METINS:
                self.dangeon_actions.kill_metins(8)
                continue

            if context.state == DangeonState.KILL_MINI_BOSS:
                self.dangeon_actions.kill_mini_boss(7)
                continue

            if context.state == DangeonState.SECOND_ARENA:
                self.dangeon_actions.enter_arena("second_arena")
                continue

            if context.state == DangeonState.SECOND_KILL_MOBS:
                self.dangeon_actions.kill_mobs(66)
                continue

            if context.state == DangeonState.SECOND_METINS:
                self.dangeon_actions.kill_metins(4, True, 0.55)
                continue

            if context.state == DangeonState.SECOND_CLICK_ITEMS:
                self.dangeon_actions.click_items(ERVELIA_DANG75_IMAGE_PATHS["dangeon_item"])
                continue

            if context.state == DangeonState.THIRD_ARENA:
                self.dangeon_actions.enter_arena("third_arena")
                continue

            if context.state == DangeonState.THIRD_KILL_MOBS:
                self.dangeon_actions.kill_mobs(76)
                continue
            if context.state == DangeonState.THIRD_METINS:
                self.dangeon_actions.kill_metins(6, True, 0.55)
                continue
            if context.state == DangeonState.THIRD_KILL_MINI_BOSS:
                self.dangeon_actions.kill_mini_boss(10)
                continue
            
            if context.state == DangeonState.END_BOSS:
                self.dangeon_actions.end_boss(95)
                continue