from collections import deque
from datetime import datetime

class Lane:
    def __init__(self, name):
        self.cars = deque()
        self.time_since_green = 0
        self.name = name
        # random high number
        self.time_since_green = 5000

    def update(self):
        self.time_since_green += 1

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
        self.time_since_green = 0
        try:
            #print ('Green lane ' + self.name)
            car = self.cars.pop()
            #print(car)
            return car
        except IndexError:
            print('Trying to green emoty queue')
