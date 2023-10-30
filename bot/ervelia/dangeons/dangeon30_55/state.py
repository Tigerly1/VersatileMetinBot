import enum

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
    LOGGING = 11
    INITIALIZING = 999
    