from random import randint

class FifoScheduler:
    def __init__(self, north, south, west, east, time_steps_per_hour):
        self.north = north
        self.south = south
        self.west = west
        self.east = east
        self.interval_length = 12
        self.count = 0
        self.direction_north = True

    def schedule(self):
        if (self.direction_north):
            try:
                self.east.pop()                   
            except IndexError:                
                pass
            try:
                self.west.pop()   
            except IndexError:                
                pass
        else:
            try:
                self.north.pop()                
            except IndexError:                
                pass
            try:
                self.south.pop()                                
            except IndexError:                
                pass
        self.count += 1

        if(self.count >= self.interval_length):
            self.direction_north = not(self.direction_north)
            self.count = 0
 
if __name__ == "__main__":
    pass