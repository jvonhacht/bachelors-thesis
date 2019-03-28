from entities import Direction

class FixedScheduler:
    def __init__(self, simulator, timesteps_per_hour):
        self.simulator = simulator
        self.period = timesteps_per_hour/30
        self.count = 0

    def schedule(self):
        if (self.count >= 0):
            if (self.count < self.period/4):
                self.simulator.green_light(Direction.SOUTH, 'left')
                self.simulator.green_light(Direction.SOUTH, 'straight_right')
            elif (self.count >= self.period/4 and self.count < self.period/2):
                self.simulator.green_light(Direction.NORTH, 'left')
                self.simulator.green_light(Direction.NORTH, 'straight_right')
            elif (self.count >= self.period/2 and self.count < self.period/4*3):
                self.simulator.green_light(Direction.WEST, 'left')
                self.simulator.green_light(Direction.WEST, 'straight_right')
            elif (self.count >= self.period/4*3 and self.count < self.period):
                self.simulator.green_light(Direction.EAST, 'left')
                self.simulator.green_light(Direction.EAST, 'straight_right')
            else:
                self.count = -4
        self.count += 1