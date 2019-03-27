import time
import numpy as np
import matplotlib.pyplot as plt
import random
from random import randint

from entities import Direction
from entities import Lane


class Simulator:

    # PARAMETERS
    time_steps_per_hour = 36000
    car_add_frequency = 50
    time_to_move = 10

    def __init__(self, *args, **kwargs):
        self.traffic_probability = self.fit_curve(False)
        self.lanes = {
            Direction.NORTH: Lane('North', Direction.EAST),
            Direction.SOUTH: Lane('South', Direction.WEST),
            Direction.WEST: Lane('West', Direction.NORTH),
            Direction.EAST: Lane('East', Direction.SOUTH)
        }
        self.time = 0
        # 3x3 matrix
        self.occupation_matrix = np.matrix('None,None,None; None,None,None; None,None,None', dtype=Car)

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
            car = None
            direction = None
            if (r_number == 0):
                direction = Direction.WEST
                car = Car(self.get_random_direction(direction), self.time)  
            elif (r_number == 1):
                direction = Direction.EAST
                car = Car(self.get_random_direction(direction), self.time)  
            elif (r_number == 2):
                direction = Direction.SOUTH
                car = Car(self.get_random_direction(direction), self.time)  
            elif (r_number == 3):   
                direction = Direction.NORTH
                car = Car(self.get_random_direction(direction), self.time)  

            if (car.destination == self.lanes[direction].left_turn):
                self.lanes[direction].left.append(car)
            else:
                self.lanes[direction].straight_right.append(car)

    def add_direction(self, direction):
        car = Car(self.get_random_direction(direction), self.time) 
        print('Added: ' + str(direction) + str(car))  

        if (car.destination == self.lanes[direction].left_turn):
            self.lanes[direction].left.append(car)
        else:
            self.lanes[direction].straight_right.append(car)

    def get_random_direction(self, direction_from):
        directions = [Direction.NORTH, Direction.SOUTH, Direction.WEST, Direction.EAST]
        directions.remove(direction_from)
        return directions[randint(0,2)] 
        # quite ugly but more effective..
        """
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
        """
    
    def green_light(self, direction, lane_type):
        car = None
        if (lane_type == 'left'):
            car = self.lanes[direction].peek_left()
        elif (lane_type == 'straight_right'):
            car = self.lanes[direction].peek_straight_right()

        if (car != None):
            allocated = self.allocate_path(direction, car.destination, car)
            if (allocated):
                if (lane_type == 'left'):
                    car = self.lanes[direction].left.pop()
                elif (lane_type == 'straight_right'):
                    car = self.lanes[direction].straight_right.pop()

    def allocate_path(self, direction_from, direction_to, car):
        if (direction_from == Direction.NORTH):
            if (direction_to == Direction.EAST):
                if (self.occupation_matrix[0,2] == None):
                    car.directions = [(Direction.EAST, self.time_to_move)]
                    self.occupation_matrix[0,2] = car
                    return True
                else:
                    return False
        # TODO 100 million if statements

    def update_occupation_matrix(self):
        for i in range(0,3):
            for j in range(0,3):
                car = self.occupation_matrix[i,j]
                if (car != None):
                    moved, direction, moves_left = car.move()
                    if (moved):
                        if (moves_left == 0):
                            self.occupation_matrix[i,j] = None
                        else:
                            if (direction == Direction.WEST):
                                self.occupation_matrix[i,j-1] = self.occupation_matrix[i,j]
                            elif (direction == Direction.EAST):
                                self.occupation_matrix[i,j+1] = self.occupation_matrix[i,j]
                            elif (direction == Direction.NORTH):
                                self.occupation_matrix[i+1,j] = self.occupation_matrix[i,j]
                            elif (direction == Direction.SOUTH):
                                self.occupation_matrix[i-1,j] = self.occupation_matrix[i,j]
                            self.occupation_matrix[i,j] = None
        print(self.occupation_matrix)

    def run(self, scheduler, stats=False):
        if (stats):
            self.X = []
            self.nY_left = []
            self.nY_straight_right = []
            self.nY_total = []
            self.sY_left = []
            self.sY_straight_right = []
            self.sY_total = []
            self.wY_left = []
            self.wY_straight_right = []
            self.wY_total = []
            self.eY_left = []
            self.eY_straight_right = []
            self.eY_total = []

        while (self.time < self.time_steps_per_hour*24):
            self.update_occupation_matrix()
            hour = self.time / self.time_steps_per_hour

            self.add_direction(Direction.NORTH)
            if (self.time % self.car_add_frequency == 0):
                #self.stochastic_add(hour)
                if (stats):
                    self.save_stats(hour)
            self.time += 1
            self.green_light(Direction.NORTH, 'left')
            time.sleep(2)

        if (stats):
            self.display_stats()


    def save_stats(self, hour):
        self.X.append(hour)
        self.nY_left.append(len(self.lanes[Direction.NORTH].left))
        self.nY_straight_right.append(len(self.lanes[Direction.NORTH].straight_right))
        self.nY_total.append(len(self.lanes[Direction.NORTH].left) + len(self.lanes[Direction.NORTH].straight_right))

        self.wY_left.append(len(self.lanes[Direction.WEST].left))
        self.wY_straight_right.append(len(self.lanes[Direction.WEST].straight_right))
        self.wY_total.append(len(self.lanes[Direction.WEST].left) + len(self.lanes[Direction.WEST].straight_right))

        self.eY_left.append(len(self.lanes[Direction.EAST].left))
        self.eY_straight_right.append(len(self.lanes[Direction.EAST].straight_right))
        self.eY_total.append(len(self.lanes[Direction.EAST].left) + len(self.lanes[Direction.EAST].straight_right))

        self.sY_left.append(len(self.lanes[Direction.SOUTH].left))
        self.sY_straight_right.append(len(self.lanes[Direction.SOUTH].straight_right))
        self.sY_total.append(len(self.lanes[Direction.SOUTH].left) + len(self.lanes[Direction.SOUTH].straight_right))

    def display_stats(self):
        color_1 = '--b'
        color_2 = '--g'
        color_3 = 'r'
        plt.subplot(4,1,1)
        plt.plot(self.X, self.nY_total, color_3,label='Total')
        plt.plot(self.X, self.nY_left, color_1,label='North left')
        plt.plot(self.X, self.nY_straight_right, color_2,label='North straight/right')
        plt.legend(loc='upper left')
        plt.subplot(4,1,2)
        plt.plot(self.X, self.sY_total, color_3,label='Total')
        plt.plot(self.X, self.sY_left, color_1, label='South left')
        plt.plot(self.X, self.sY_straight_right, color_2, label='South straight/right')
        plt.legend(loc='upper left')
        plt.subplot(4,1,3)
        plt.plot(self.X, self.wY_total, color_3,label='Total')
        plt.plot(self.X, self.wY_left, color_1, label='West left')
        plt.plot(self.X, self.wY_straight_right, color_2, label='West straight/right')
        plt.legend(loc='upper left')
        plt.subplot(4,1,4)
        plt.plot(self.X, self.eY_total, color_3,label='Total')
        plt.plot(self.X, self.eY_left, color_1, label='East left')
        plt.plot(self.X, self.eY_straight_right, color_2, label='East straight/right')
        plt.legend(loc='upper left')
        plt.show()

class Car:
    def __init__(self, destination, arrival):
        self.destination = destination
        self.arrival = arrival
        self.directions = []
        self.counter = 0

    def move(self):
        direction = self.directions[0]
        if (self.counter >= direction[1]):
            self.directions.pop()
            self.counter = 0
            return True, direction[0], len(self.directions)

        self.counter += 1
        return False, None, len(self.directions)
    
    def __str__(self):
        return '[d: ' + str(self.destination) + ' - arr: ' + str(self.arrival) + ']'

if __name__ == "__main__":
    simulator = Simulator()
    simulator.run(None, stats=True)
