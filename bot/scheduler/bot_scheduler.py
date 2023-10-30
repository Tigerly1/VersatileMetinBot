class BotScheduler:
    def __init__(self):
        self.current_bot = None
        self.bots = []

    def add_bot(self, bot):
        self.bots.append(bot)

    def get_next_bot(self):
        if not self.bots:
            return None
        if self.current_bot is None:
            self.current_bot = self.bots[0]
        else:
            curr_index = self.bots.index(self.current_bot)
            next_index = (curr_index + 1) % len(self.bots)
            self.current_bot = self.bots[next_index]
        return self.current_bot
