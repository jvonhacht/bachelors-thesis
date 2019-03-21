from collections import deque
from datetime import datetime
from random import randint
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
import time

class Simulator:
    time_to_drive = 5
    time_steps_per_hours = 600

    def __init__(self, *args, **kwargs):
        self.south = deque()
        self.north = deque()
        self.west = deque()
        self.east = deque()
        self.traffic_probability = self.fit_curve(False)

    def fit_curve(self, graph):
        points = np.array([(0, 50.), (1, 40), (2, 30), (3, 25),
                           (4, 30), (5, 35), (6, 60), (7, 150), 
                           (8, 500), (9, 520), (10, 600), (11, 600),
                           (12, 475), (13, 380), (14, 350), (15, 400),
                           (16, 500), (17, 550), (18, 550), (19, 350),
                           (20, 275), (21, 190), (22, 150), (23, 125), 
                           (24, 90)])
        points = self.normalize_tuple_y(points)
        # get x and y vectors
        x = points[:,0]
        y = points[:,1]

        # calculate polynomial
        z = np.polyfit(x, y, 11)
        f = np.poly1d(z)
        # calculate new x's and y's
        if (graph):
            x_new = np.linspace(x[0], x[-1], 50)
            y_new = f(x_new)

            plt.plot(x,y,'o', x_new, y_new)
            plt.xlim([x[0]-1, x[-1] + 1 ])
            plt.show()
        return f

    def normalize_tuple_y(self, tuple_list):
        max = 0
        for element in tuple_list:
            if (element[1] > max):
                max = element[1]
        for element in tuple_list:
            element[1] = element[1]/max
        return tuple_list

    def stochastic_add(self, hour):
        r_number = random.uniform(0, 1)
        if (r_number <= self.traffic_probability(hour)):
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

    def timestep(self, hour):
        # maybe create schedular object here
        # and call a method, handle traffic
        self.stochastic_add(hour)
        #time.sleep(0.2)

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
    
    def run(self):
        count = 0
        prev_hour = 0
        prev_size = 0
        while (count < self.time_steps_per_hours*24):
            hour = round(count / self.time_steps_per_hours)
            self.timestep(hour)
            count += 1
            if (prev_hour != hour):
                prev_hour = hour
                print('number of cars hour ' + str(hour) + ' lane north: ' + str(len(self.north)-prev_size))
                prev_size = len(self.north)
        #print(self)

class Car:
    def __init__(self, direction):
        self.direction = direction
        self.arrival = datetime.now()
    
    def __str__(self):
        return '[d: ' + self.direction + ' - arr: ' + str(self.arrival) + ']'


if __name__ == "__main__":
    simulator = Simulator()
    simulator.run()