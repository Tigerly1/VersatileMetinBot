import random
import time
from bot.ervelia.dangeons.dangeon30_55.state import DangeonState
from bot.ervelia.dangeons.dangeon30_55.state_actions.actions import Actions
from typing import TYPE_CHECKING

from bot.interfaces.dungeon_strategy_interface import DangeonStateStrategy
if TYPE_CHECKING:
    from bot.core_loop import MetinBot  # This import is only for type checking

class Dangeon30StateOrder(DangeonStateStrategy):
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
        if label == "first_arena":
            y = y + 45
            if x > 30:
                x = x - 30 
            context.metin_window.mouse_move(x,y)
            
        if label == "second_arena":
            if  x > 650:
                context.game_actions.rotate_view(small_rotation=True)
                self.time_of_new_screen = time.time()
                return False, False
            elif x < 270:
                context.game_actions.rotate_view(small_rotation=True, rotate_right=True)
                context.time_of_new_screen = time.time()
                return False, False

        return x, y

    def execute_actions_by_state(self, context: "MetinBot"):
        time.sleep(0.02)
        while not context.stopped:

            ## DO THE HEALTH CHECKS IN SEPERATE THREAD ALSO TO NOT BLOCK THE CLICKING
            context.health_checks_iterations = (context.health_checks_iterations + 1) % 50

            if context.health_checks_iterations == 45 or context.health_checks_bool:
                context.game_actions.health_checks()
                context.health_checks_bool = False
                continue 
            
            if context.state == DangeonState.INITIALIZING:
                context.metin_window.activate()
                context.game_actions.calibrate_view("guard")
                context.game_actions.get_the_player_on_the_horse()
                context.game_actions.zoom_out()
                context.game_actions.remove_dangon_items_from_inv()
                context.switch_state(DangeonState.ENTER_THE_DANGEON)
                continue

            if context.state == DangeonState.DEBUG:

                context.osk_window.mouse_move(690,93)
                time.sleep(5)
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
                self.dangeon_actions.first_arena()
                continue

            if context.state == DangeonState.KILL_MOBS:
                self.dangeon_actions.kill_mobs()
                continue

            if context.state == DangeonState.KILL_METINS:
                self.dangeon_actions.kill_metins()
                continue

            if context.state == DangeonState.KILL_MINI_BOSS:
                self.dangeon_actions.kill_mini_boss()
                continue

            if context.state == DangeonState.SECOND_ARENA:
                self.dangeon_actions.second_arena()
                continue

            if context.state == DangeonState.GATHER_ITEMS:
                self.dangeon_actions.gather_items()
                continue

            if context.state == DangeonState.SECOND_METINS:
                self.dangeon_actions.second_metins()
                continue

            if context.state == DangeonState.SECOND_MINI_BOSS:
                self.dangeon_actions.second_mini_boss()
                continue
            
            if context.state == DangeonState.END_BOSS:
                self.dangeon_actions.end_boss()
                continue