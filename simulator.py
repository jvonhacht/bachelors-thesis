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

    def randomAdd(self):
        r_number = randint(0,3)
        if (r_number == 0):
            self.north.append(Car('west'))
        elif (r_number == 1):
            self.south.append(Car('west'))
        elif (r_number == 2):
            self.west.append(Car('west'))
        elif (r_number == 3):
            self.east.append(Car('west'))
        pass

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
    simulator.randomAdd()
    simulator.randomAdd()
    simulator.randomAdd()
    simulator.randomAdd()
    print(simulator)
    #