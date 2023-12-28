import requests

from dotenv import load_dotenv
import os

load_dotenv()

import logging

# Configure logging
logging.basicConfig(filename="debug", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class DungeonBotStatistics:

    _instance = None

    def __init__(self):
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not self.telegram_bot_token or not self.telegram_chat_id:
            raise ValueError("The Telegram bot token or chat ID has not been set in the environment variables.")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DungeonBotStatistics, cls).__new__(cls)
            # Initialize our instance / object
            cls._instance.dungeons_completed = 0
            cls._instance.total_dungeon_time = 0.0
            cls._instance.bugs_encountered = 0
            cls._instance.state_times = {}
            cls._instance.window_foreground_time_in_state = {}
        return cls._instance

    def add_dungeon_completed(self, time_spent):
        self.dungeons_completed += 1
        self.total_dungeon_time += time_spent
        if self.dungeons_completed % 5 == 0:
            self.notify_via_telegram("{} dungeons completed!".format(self.dungeons_completed))

    def add_bug_encountered(self):
        self.bugs_encountered += 1

    def add_window_foreground_time_in_state(self, state_name, time_spent):
        if state_name not in self.window_foreground_time_in_state:
            self.window_foreground_time_in_state[state_name] = []
        self.window_foreground_time_in_state[state_name].append(time_spent)

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
        print("Average Time in turned on window:")
        for state, times in self.average_time_in_foreground_window_state.items():
            print(f" - {state}: {times:.2f} seconds")
        print("Average time interacting with window by one account in dangeon")
        times = self.average_time_in_foreground_window_state.values()
        avg_time_interacting = sum(times)
        print(f" - {avg_time_interacting:.2f} seconds")
    def notify_via_telegram(self, message):
        # Replace 'your_bot_token' with your actual bot token and 'your_chat_id' with your actual chat ID
        send_message_url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        requests.post(send_message_url, data={
            "chat_id": self.telegram_chat_id,
            "text": message
        })

    @property
    def average_dungeon_time(self):
        return self.total_dungeon_time / self.dungeons_completed if self.dungeons_completed else 0

    @property
    def average_time_in_state(self):
        return {
            state: sum(times) / len(times) for state, times in self.state_times.items()
        }
    
    @property
    def average_time_in_foreground_window_state(self):
        return {
            state: sum(times) / len(times) for state, times in self.window_foreground_time_in_state.items()
        }
# Usage:
# stats = DungeonBotStatistics()
# stats.add_dungeon_completed(30)
# stats.add_bug_encountered()
# stats.add_state_time("state1", 5)
# print(stats.average_dungeon_time)
# print(stats.average_time_in_state)
