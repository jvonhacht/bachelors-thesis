from entities import Direction

class FixedScheduler:
    def __init__(self, simulator, timesteps_per_hour):
        self.simulator = simulator
        self.period = timesteps_per_hour/30
        self.count = 0

    def schedule(self):
        if (self.count >= 0):
            if (self.count < self.period/4):
                if (self.count % 2 == 1):
                    self.simulator.step(0)
                else:
                    self.simulator.step(1)
            elif (self.count >= self.period/4 and self.count < self.period/2):
                if (self.count % 2 == 1):
                    self.simulator.step(2)
                else:
                    self.simulator.step(3)
            elif (self.count >= self.period/2 and self.count < self.period/4*3):
                if (self.count % 2 == 1):
                    self.simulator.step(4)
                else:
                    self.simulator.step(5)
            elif (self.count >= self.period/4*3 and self.count < self.period):
                if (self.count % 2 == 1):
                    self.simulator.step(6)
                else:
                    self.simulator.step(7)
            else:
                self.count = -4
        self.count += 1