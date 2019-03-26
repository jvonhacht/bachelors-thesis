from collections import deque
from datetime import datetime

class Lane:
    def __init__(self):
        self.cars = deque()
        self.time_since_green = 0

    def update(self):
        self.time_since_green -= 1

    def size(self):
        return len(self.cars)

    def add_car(self, car):
        self.cars.append(car)

    def get_cars(self):
        return self.cars

    def peek_car(self):
        if self.cars:
            return self.cars[-1]

    def green(self):
        return self.cars.pop()
