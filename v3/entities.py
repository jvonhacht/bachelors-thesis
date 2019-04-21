from collections import deque
from enum import Enum

class Direction(Enum):
    NORTH = 1
    SOUTH = 2
    EAST = 3
    WEST = 4
    NONE = 5

class Traffic(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Lane:
    def __init__(self, name):
        self.name = name
        self.left = deque()
        self.straight_right = deque()     
        self.passed_cars = 0           

    def size(self):
        return len(self.left) + len(self.straight_right)

    def peek_straight_right(self):
        if self.straight_right:
            return self.straight_right[0]
        return -1

    def peek_left(self):
        if self.left:
            return self.left[0]
        return -1

    def get_total_wait_time(self):
        total_wait = 0
        for time in self.straight_right:
            total_wait += time
        for time in self.left:
            total_wait += time
        return total_wait

    def __str__(self):
        return self.name + ', car amount: ' + str(self.size()) 