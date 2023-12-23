from abc import ABC, abstractmethod

class DangeonStateStrategy(ABC):
    @abstractmethod
    def execute_actions_by_state(self, context):
        pass
    @abstractmethod
    def get_first_state(self):
        pass
    @abstractmethod
    def get_last_state_from_iteration(self):
        pass
    @abstractmethod
    def get_next_state(self, state):
        pass
    @abstractmethod
    def get_logging_state(self):
        pass
    @abstractmethod
    def get_initializing_state(self):
        pass
    @abstractmethod
    def init_actions_passing_variables(self, context):
        pass