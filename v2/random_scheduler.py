import random
from entities import Direction

class RandomScheduler:
    def schedule(self):
        return random.randint(0,7)