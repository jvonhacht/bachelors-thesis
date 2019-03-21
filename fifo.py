from random import randint

class FifoScheduler:
    def __init__(self, north, south, west, east):
        self.north = north
        self.south = south
        self.west = west
        self.east = east

    def schedule(self):
        r_number = randint(0,3)
        if (r_number == 0):
            try:
                self.north.pop()
            except Exception:
                pass
        elif (r_number == 1):
            try:
                self.south.pop()
            except Exception:
                pass
        elif (r_number == 2):
            try:
                self.west.pop()
            except Exception:
                pass
        elif (r_number == 3):
            try:
                self.east.pop()
            except Exception:
                pass

if __name__ == "__main__":
    pass