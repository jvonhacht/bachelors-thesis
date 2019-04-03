from collections import deque
from enum import Enum

class Direction(Enum):
    NORTH = 1
    SOUTH = 2
    EAST = 3
    WEST = 4

class Lane:
    def __init__(self, name, left_turn):
        self.left = deque()
        self.straight_right = deque()
        self.left_turn = left_turn
        self.name = name

    def size(self):
        return len(self.left) + len(self.straight_right)

    def peek_straight_right(self):
        if self.straight_right:
            return self.straight_right[-1]
        return -1

    def peek_left(self):
        if self.left:
            return self.left[-1]
        return -1

    def __str__(self):
        return self.name + ': ' + str(self.size()) + 'cars left' 