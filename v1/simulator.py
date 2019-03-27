from collections import deque
from datetime import datetime
from random import randint
import random
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
import time
from fifo import FifoScheduler
from lane import Lane
from direction import Direction
import tkinter

class Simulator():
    time_steps_per_hours = 36000
    # short refers to closest exit and long to exit furthest away
    time_car_drive_short = 30
    time_car_drive_straight = 45
    time_car_drive_long = 60
    # it takes 50% less time to pass if the car in front is moving
    time_rolling_multiplier = 0.5
    time_between_rolling = 5

    # not occupied if 0
    occupied_upper_left = 0
    occupied_upper_right = 0
    occupied_lower_left = 0
    occupied_lower_right = 0

    previous_green = Direction.SOUTH

    def __init__(self, *args, **kwargs):
        self.south = Lane("south")
        self.north = Lane("north")
        self.west = Lane("west")
        self.east = Lane("east")
        self.traffic_probability = self.fit_curve(False)
        self.time = 0
        #self.setup_GUI()

    def setup_GUI(self):
        self.root = tkinter.Tk()
        self.ul = tkinter.IntVar()
        self.ul.set(0)
        self.ur = tkinter.IntVar()
        self.ur.set(0)
        self.ll = tkinter.IntVar()
        self.ll.set(0)
        self.lr = tkinter.IntVar()
        self.lr.set(0)
        l = tkinter.Label(self.root,textvariable="Testing")
        l.pack()
        #tkinter.Label(self.root, textvariable=self.ul).grid(row = 0, column=0)
        #tkinter.Label(self.root, textvariable=self.ur).grid(row = 0, column=1)
        #tkinter.Label(self.root, textvariable=self.ll).grid(row = 1, column=0)
        #tkinter.Label(self.root, textvariable=self.lr).grid(row = 1, column=1)

    def set_values(self, ul, ur, ll, lr):
        self.ul.set(ul)
        self.ur.set(ur)
        self.ll.set(ll)
        self.lr.set(lr)

    def fit_curve(self, graph):
        """
        Fit a curve to traffic data points.

        Parameters
        ----------
        graph : bool
            show curve graph or not

        Returns
        -------
        function
            function that calculates traffic probability
        """
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
        """
        Normalize the second value (y value) in the tuple.

        Parameters
        ----------
        tuple_list : list
            list of tuples

        Returns
        -------
        list
            list of y normalized tuples
        """
        max = 0
        for element in tuple_list:
            if (element[1] > max):
                max = element[1]
        for element in tuple_list:
            element[1] = element[1]/max
        return tuple_list

    def stochastic_add(self, hour):
        """
        Add car to a random lane following traffic probability function.

        Parameters
        ----------
        hour : float
            hour of day
        """
        r_number = random.uniform(0, 1)
        if (r_number <= self.traffic_probability(hour)):  
            r_number = randint(0,3)
            if (r_number == 0):
                self.west.add_car(Car(self.get_random_direction(Direction.WEST), self.time))
            elif (r_number == 1):
                self.south.add_car(Car(self.get_random_direction(Direction.SOUTH), self.time))
            elif (r_number == 2):
                self.north.add_car(Car(self.get_random_direction(Direction.NORTH), self.time))
            elif (r_number == 3):   
                self.east.add_car(Car(self.get_random_direction(Direction.EAST), self.time))

    def add_direction(self, direction):
        if (direction == Direction.WEST):
            self.west.add_car(Car(self.get_random_direction(Direction.WEST), self.time))
            #print('Car added west')
        elif (direction == Direction.SOUTH):
            self.south.add_car(Car(self.get_random_direction(Direction.SOUTH), self.time))
            #print('Car added south')
        elif (direction == Direction.NORTH):
            self.north.add_car(Car(self.get_random_direction(Direction.NORTH), self.time))
            #print('Car added north')
        elif (direction == Direction.EAST):   
            self.east.add_car(Car(self.get_random_direction(Direction.EAST), self.time))
            #print('Car added east')

    def get_random_direction(self, direction_from):
        r_number = randint(0,2)
        if (direction_from == Direction.NORTH):
            if (r_number == 0):
                return Direction.SOUTH
            elif (r_number == 1):
                return Direction.EAST
            elif (r_number == 2):
                return Direction.WEST
        elif(direction_from == Direction.SOUTH):
            if (r_number == 0):
                return Direction.NORTH
            elif (r_number == 1):
                return Direction.EAST
            elif (r_number == 2):
                return Direction.WEST
        elif(direction_from == Direction.EAST):
            if (r_number == 0):
                return Direction.SOUTH
            elif (r_number == 1):
                return Direction.NORTH
            elif (r_number == 2):
                return Direction.WEST
        elif(direction_from == Direction.WEST):
            if (r_number == 0):
                return Direction.SOUTH
            elif (r_number == 1):
                return Direction.EAST
            elif (r_number == 2):
                return Direction.NORTH

    def green(self, lane):
        # TODO check occupancy can be false if from the same lane
        # TODO A function that update_occupancy(from, to) w/ time variables
        if (lane == Direction.NORTH):
            car = self.north.peek_car()
            # car can go
            #print(self.previous_green)
            #print(self.previous_green == lane)
            #print(self.check_occupancy(lane, car.direction))
            if car != None and ((self.check_occupancy(lane, car.direction) or self.previous_green == lane)):
                self.set_occupancy(lane, car.direction, self.previous_green == lane)
                if (self.previous_green == lane): 
                    if (self.north.time_since_green >= self.time_between_rolling):
                        self.north.green()
                        self.previous_green = lane
                else:
                    self.north.green()
                    self.previous_green = lane
        elif(lane == Direction.SOUTH):
            car = self.south.peek_car()
            # car can go
            if (car != None and (self.check_occupancy(lane, car.direction) or self.previous_green == lane)):
                self.set_occupancy(lane, car.direction, self.previous_green == lane)
                if (self.previous_green == lane): 
                    if (self.south.time_since_green >= self.time_between_rolling):
                        self.south.green()
                        self.previous_green = lane
                else:
                    self.south.green()
                    self.previous_green = lane
        elif(lane == Direction.WEST):
            car = self.west.peek_car()
            # car can go
            if (car != None and (self.check_occupancy(lane, car.direction) or self.previous_green == lane)):
                self.set_occupancy(lane, car.direction, self.previous_green == lane)
                if (self.previous_green == lane): 
                    if (self.west.time_since_green >= self.time_between_rolling):
                        self.west.green()
                        self.previous_green = lane
                else:
                    self.west.green()
                    self.previous_green = lane
        elif(lane == Direction.EAST):
            car = self.east.peek_car()
            # car can go
            if (car != None and (self.check_occupancy(lane, car.direction) or self.previous_green == lane)):
                self.set_occupancy(lane, car.direction, self.previous_green == lane)
                if (self.previous_green == lane): 
                    if (self.east.time_since_green >= self.time_between_rolling):
                        self.east.green()
                        self.previous_green = lane
                else:
                    self.east.green()
                    self.previous_green = lane

    def check_occupancy(self, direction_from, direction_to):
        if (direction_from == Direction.NORTH):
            if (direction_to == Direction.WEST):
                return self.occupied_upper_left == 0
            elif (direction_to == Direction.EAST):
                return (self.occupied_upper_left == 0 and 
                        self.occupied_lower_left == 0 and 
                        self.occupied_lower_right == 0)
            elif (direction_to == Direction.SOUTH):
                return (self.occupied_upper_left == 0 and 
                        self.occupied_lower_left == 0)
        elif (direction_from == Direction.SOUTH):
            if (direction_to == Direction.WEST):
                return (self.occupied_upper_left == 0 and 
                        self.occupied_upper_right == 0 and 
                        self.occupied_lower_right == 0)
            elif (direction_to == Direction.EAST):
                return self.occupied_lower_right == 0
            elif (direction_to == Direction.NORTH):
                return (self.occupied_upper_right == 0 and 
                        self.occupied_lower_right == 0)
        elif (direction_from == Direction.WEST):
            if (direction_to == Direction.NORTH):
                return (self.occupied_lower_left == 0 and 
                        self.occupied_lower_right == 0 and 
                        self.occupied_upper_right == 0)
            elif (direction_to == Direction.SOUTH):
                return self.occupied_lower_left == 0
            elif (direction_to == Direction.EAST):
                return (self.occupied_lower_left == 0 and 
                        self.occupied_lower_right == 0)
        elif (direction_from == Direction.EAST):
            if (direction_to == Direction.SOUTH):
                return (self.occupied_upper_left == 0 and 
                        self.occupied_upper_right == 0 and 
                        self.occupied_lower_left == 0)
            elif (direction_to == Direction.NORTH):
                return self.occupied_upper_left == 0
            elif (direction_to == Direction.WEST):
                return (self.occupied_upper_left == 0 and 
                        self.occupied_upper_right == 0)

    def set_occupancy(self, direction_from, direction_to, reduced):
        multiplier = 1
        if (reduced):
            multiplier = self.time_rolling_multiplier
        # literally puke, is there a neater way to do this?..
        if (direction_from == Direction.NORTH):
            if (direction_to == Direction.WEST):
                if (self.time_car_drive_short*multiplier > self.occupied_upper_left):
                    self.occupied_upper_left = self.time_car_drive_short*multiplier
            elif (direction_to == Direction.EAST):
                if (self.time_car_drive_long*multiplier > self.occupied_upper_left):
                    self.occupied_upper_left = self.time_car_drive_long*multiplier
                if (self.time_car_drive_long*multiplier > self.occupied_lower_left):
                    self.occupied_lower_left = self.time_car_drive_long*multiplier
                if (self.time_car_drive_long*multiplier > self.occupied_lower_right):
                    self.occupied_lower_right = self.time_car_drive_long*multiplier
            elif (direction_to == Direction.SOUTH):
                if (self.time_car_drive_straight*multiplier > self.occupied_upper_left):
                    self.occupied_upper_left = self.time_car_drive_straight*multiplier
                if (self.time_car_drive_straight*multiplier > self.occupied_lower_left):
                    self.occupied_lower_left = self.time_car_drive_straight*multiplier
        elif (direction_from == Direction.SOUTH):
            if (direction_to == Direction.WEST):
                if (self.time_car_drive_long*multiplier > self.occupied_upper_left):
                    self.occupied_upper_left = self.time_car_drive_long*multiplier
                if (self.time_car_drive_long*multiplier > self.occupied_upper_right):
                    self.occupied_upper_right = self.time_car_drive_long*multiplier
                if (self.time_car_drive_long*multiplier > self.occupied_lower_right):
                    self.occupied_lower_right = self.time_car_drive_long*multiplier
            elif (direction_to == Direction.EAST):
                if (self.time_car_drive_short*multiplier > self.occupied_lower_right):
                    self.occupied_lower_right = self.time_car_drive_short*multiplier
            elif (direction_to == Direction.NORTH):
                if (self.time_car_drive_straight*multiplier > self.occupied_upper_right):
                    self.occupied_upper_right = self.time_car_drive_straight*multiplier
                if (self.time_car_drive_straight*multiplier > self.occupied_lower_right):
                    self.occupied_lower_right = self.time_car_drive_straight*multiplier
        elif (direction_from == Direction.WEST):
            if (direction_to == Direction.NORTH):
                if (self.time_car_drive_long*multiplier > self.occupied_lower_left):
                    self.occupied_lower_left = self.time_car_drive_long*multiplier
                if (self.time_car_drive_long*multiplier > self.occupied_lower_right):
                    self.occupied_lower_right = self.time_car_drive_long*multiplier
                if (self.time_car_drive_long*multiplier > self.occupied_upper_right):
                    self.occupied_upper_right = self.time_car_drive_long*multiplier
            elif (direction_to == Direction.SOUTH):
                if (self.time_car_drive_short*multiplier > self.occupied_lower_left):
                    self.occupied_lower_left = self.time_car_drive_short*multiplier
            elif (direction_to == Direction.EAST):
                if (self.time_car_drive_straight*multiplier > self.occupied_lower_left):
                    self.occupied_lower_left = self.time_car_drive_straight*multiplier
                if (self.time_car_drive_straight*multiplier > self.occupied_lower_right):
                    self.occupied_lower_right = self.time_car_drive_straight*multiplier
        elif (direction_from == Direction.EAST):
            if (direction_to == Direction.SOUTH):
                if (self.time_car_drive_long*multiplier > self.occupied_upper_left):
                    self.occupied_upper_left = self.time_car_drive_long*multiplier
                if (self.time_car_drive_long*multiplier > self.occupied_upper_right):
                    self.occupied_upper_right = self.time_car_drive_long*multiplier
                if (self.time_car_drive_long*multiplier > self.occupied_lower_left):
                    self.occupied_lower_left = self.time_car_drive_long*multiplier
            elif (direction_to == Direction.NORTH):
                if (self.time_car_drive_short*multiplier > self.occupied_upper_left):
                    self.occupied_upper_left = self.time_car_drive_short*multiplier
            elif (direction_to == Direction.WEST):
                if (self.time_car_drive_straight*multiplier > self.occupied_upper_left):
                    self.occupied_upper_left = self.time_car_drive_straight*multiplier
                if (self.time_car_drive_straight*multiplier > self.occupied_upper_right):
                    self.occupied_upper_right = self.time_car_drive_straight*multiplier

    def __str__(self):
        string = '======================================================================'
        string += '\nNorth: \n'
        for car in self.north.get_cars():
            string += car.__str__() + '\n'
        string += '======================================================================'
        string += '\nSouth: \n'
        for car in self.south.get_cars():
            string += car.__str__() + '\n'
        string += '======================================================================'
        string += '\nWest: \n'
        for car in self.west.get_cars():
            string += car.__str__() + '\n'
        string += '======================================================================'
        string += '\nEast: \n'
        for car in self.east.get_cars():
            string += car.__str__() + '\n'
        string += '======================================================================'
        return string
    
    def run(self, scheduler):
        count = 0
        X = []
        nY = []
        sY = []
        wY = []
        eY = []
        while (count < self.time_steps_per_hours*24):
            #time.sleep(2)
            hour = count / self.time_steps_per_hours
            #self.add_direction(Direction.SOUTH)
            if (count % 20 == 0):
                #self.stochastic_add(hour)
                self.add_direction(Direction.SOUTH)
                self.add_direction(Direction.NORTH)
                self.add_direction(Direction.WEST)
                self.add_direction(Direction.EAST)
                pass
            #self.green(Direction.SOUTH)
            scheduler.schedule()
            count += 1

            # save statistics
            X.append(hour)
            nY.append(self.north.size())
            sY.append(self.south.size())
            wY.append(self.west.size())
            eY.append(self.east.size())

            """
            self.set_values(self.occupied_upper_left, self.occupied_upper_right, 
                            self.occupied_lower_left, self.occupied_lower_right)
            self.root.update_idletasks()
            """

            # time passes
            self.time += 1
            if (self.occupied_upper_left > 0):
                self.occupied_upper_left -= 1
            if (self.occupied_upper_right > 0):
                self.occupied_upper_right -= 1
            if (self.occupied_lower_left > 0):
                self.occupied_lower_left -= 1
            if (self.occupied_lower_right >  0):
                self.occupied_lower_right -= 1
            self.north.update()
            self.south.update()
            self.west.update()
            self.east.update()

            #print('upper left: ' + str(self.occupied_upper_left))
            #print('upper right: ' + str(self.occupied_upper_right))
            #print('lower left: ' + str(self.occupied_lower_left))
            #print('lower right: ' + str(self.occupied_lower_right))

        plt.subplot(1,1,1)
        plt.plot(X, nY, label='North')
        plt.plot(X, sY, label='South')
        plt.plot(X, wY, label='West')
        plt.plot(X, eY, label='East')
        plt.legend(loc='upper left')
        plt.show()

class Car:
    def __init__(self, direction, arrival):
        self.direction = direction
        self.arrival = arrival
    
    def __str__(self):
        return '[d: ' + str(self.direction) + ' - arr: ' + str(self.arrival) + ']'


if __name__ == "__main__":
    simulator = Simulator()
    fifo = FifoScheduler(simulator, simulator.time_steps_per_hours)
    simulator.run(fifo)