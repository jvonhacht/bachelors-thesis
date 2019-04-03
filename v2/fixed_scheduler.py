from entities import Direction
import random

class FixedScheduler:
    def __init__(self, timesteps_per_hour):
        self.period = timesteps_per_hour/60
        self.count = 0

    def schedule(self):
        if (self.count >= 0):
            if (self.count < self.period/4):
                if (self.count % 2 == 1):
                    return 0
                else:
                    return 1
            elif (self.count >= self.period/4 and self.count < self.period/2):
                if (self.count % 2 == 1):
                    return 2
                else:
                    return 3
            elif (self.count >= self.period/2 and self.count < self.period/4*3):
                if (self.count % 2 == 1):
                    return 4
                else:
                    return 5
            elif (self.count >= self.period/4*3 and self.count < self.period):
                if (self.count % 2 == 1):
                    return 6
                else:
                    return 7
            else:
                self.count = -4
        self.count += 1