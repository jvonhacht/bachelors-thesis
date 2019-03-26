from random import randint
from direction import Direction

class FifoScheduler:
    def __init__(self, simulator, time_steps_per_hour):
        self.simulator = simulator
        self.interval_length = 600
        self.count = 0
        self.direction_north = True

    def schedule(self):
        if (self.direction_north):
            try:
                self.simulator.green(Direction.EAST)                   
            except IndexError:                
                pass
            try:
                self.simulator.green(Direction.WEST)   
            except IndexError:                
                pass
        else:
            try:
                self.simulator.green(Direction.NORTH)                
            except IndexError:                
                pass
            try:
                self.simulator.green(Direction.SOUTH)                                
            except IndexError:                
                pass
        self.count += 1

        if(self.count >= self.interval_length):
            self.direction_north = not(self.direction_north)
            self.count = 0
 
if __name__ == "__main__":
    pass