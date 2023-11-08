class DungeonBotStatistics:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DungeonBotStatistics, cls).__new__(cls)
            # Initialize our instance / object
            cls._instance.dungeons_completed = 0
            cls._instance.total_dungeon_time = 0.0
            cls._instance.bugs_encountered = 0
            cls._instance.state_times = {}
        return cls._instance

    def add_dungeon_completed(self, time_spent):
        self.dungeons_completed += 1
        self.total_dungeon_time += time_spent

    def add_bug_encountered(self):
        self.bugs_encountered += 1

    def add_state_time(self, state_name, time_spent):
        if state_name not in self.state_times:
            self.state_times[state_name] = []
        self.state_times[state_name].append(time_spent)

    def log_statistics(self):
        print(f"Dungeons Completed: {self.dungeons_completed}")
        print(f"Total Dungeon Time: {self.total_dungeon_time} seconds")
        if self.dungeons_completed:
            print(f"Average Dungeon Time: {self.average_dungeon_time} seconds")
        print(f"Bugs Encountered: {self.bugs_encountered}")
        print("Average Time in States:")
        for state, times in self.average_time_in_state.items():
            print(f" - {state}: {times:.2f} seconds")

    @property
    def average_dungeon_time(self):
        return self.total_dungeon_time / self.dungeons_completed if self.dungeons_completed else 0

    @property
    def average_time_in_state(self):
        return {
            state: sum(times) / len(times) for state, times in self.state_times.items()
        }

# Usage:
# stats = DungeonBotStatistics()
# stats.add_dungeon_completed(30)
# stats.add_bug_encountered()
# stats.add_state_time("state1", 5)
# print(stats.average_dungeon_time)
# print(stats.average_time_in_state)
