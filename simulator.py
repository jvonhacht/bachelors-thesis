from collections import deque
from datetime import datetime
from random import randint

class Simulator:
    time_to_drive = 5

    def __init__(self, *args, **kwargs):
        self.south = deque()
        self.north = deque()
        self.west = deque()
        self.east = deque()

    def random_add(self):
        r_number = randint(0,3)
        if (r_number == 0):
            self.north.append(Car(self.get_random_direction()))
        elif (r_number == 1):
            self.south.append(Car(self.get_random_direction()))
        elif (r_number == 2):
            self.west.append(Car(self.get_random_direction()))
        elif (r_number == 3):
            self.east.append(Car(self.get_random_direction()))

    def get_random_direction(self):
        r_number = randint(0,3)
        if (r_number == 0):
            return 'NORTH'
        elif (r_number == 1):
            return 'SOUTH'
        elif (r_number == 2):
            return 'WEST'
        elif (r_number == 3):
            return 'EAST'

    def timestep(self):
        # maybe create schedular object here
        # and call a method, handle traffic
        self.random_add()

    def __str__(self):
        string = '======================================================================'
        string += '\nNorth: \n'
        for car in self.north:
            string += car.__str__() + '\n'
        string += '======================================================================'
        string += '\nSouth: \n'
        for car in self.south:
            string += car.__str__() + '\n'
        string += '======================================================================'
        string += '\nWest: \n'
        for car in self.west:
            string += car.__str__() + '\n'
        string += '======================================================================'
        string += '\nEast: \n'
        for car in self.east:
            string += car.__str__() + '\n'
        string += '======================================================================'
        return string

class Car:
    def __init__(self, direction):
        self.direction = direction
        self.arrival = datetime.now()
    
    def __str__(self):
        return '[d: ' + self.direction + ' - arr: ' + str(self.arrival) + ']'


if __name__ == "__main__":
    simulator = Simulator()
    simulator.timestep()
    simulator.timestep()
    simulator.timestep()
    simulator.timestep()
    print(simulator)