import time
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
import random
from random import randint

from graphics import *

from entities import Direction
from entities import Lane

from fixed_scheduler import FixedScheduler
from dqn_scheduler import DQNScheduler
from random_scheduler import RandomScheduler

class Simulator:

    # PARAMETERS
    time_steps_per_hour = 18000
    car_add_frequency = 8
    time_to_move = 10

    def __init__(self, minutes, traffic='stochastic', draw=False, stats=False, save=False):
        if (traffic == 'stochastic'):
            self.traffic_probability = self.fit_curve(False)
        elif (traffic == 'heavy'):
            self.traffic_probability = lambda x: 1

        self.minutes = minutes

        self.lanes = {
            Direction.NORTH: Lane('North', Direction.EAST),
            Direction.SOUTH: Lane('South', Direction.WEST),
            Direction.WEST: Lane('West', Direction.NORTH),
            Direction.EAST: Lane('East', Direction.SOUTH)
        }
        self.time = 18000*9.5
        self.time = 0
        # 3x3 matrix
        self.occupation_matrix = np.matrix('None,None,None; None,None,None; None,None,None', dtype=Car)

        # instructions
        self.matrix_instructions = {
            Direction.SOUTH: {
                Direction.NORTH: [(2,2),(1,2),(0,2)],
                Direction.EAST: [(2,2)],
                Direction.WEST: [(2,1),(1,1),(0,1),(0,0)],
            },
            Direction.NORTH: {
                Direction.SOUTH: [(0,0),(1,0),(2,0)],
                Direction.EAST: [(0,1),(1,1),(2,1),(2,2)],
                Direction.WEST: [(0,0)],
            },
            Direction.EAST: {
                Direction.NORTH: [(0,2)],
                Direction.SOUTH: [(1,2),(1,1),(1,0),(2,0)],
                Direction.WEST: [(0,2),(0,1),(0,0)],
            },
            Direction.WEST: {
                Direction.NORTH: [(1,0),(1,1),(1,2),(0,2)],
                Direction.SOUTH: [(2,0)],
                Direction.EAST: [(2,0),(2,1),(2,2)],
            }
        }
        self.stats = stats
        # graphics
        self.draw = draw
        if (self.draw):
            self.win = GraphWin('Test', 500, 500)

        # variables for average waiting time
        self.waiting_time = []
        self.waiting_time_dict = {
            Direction.NORTH: {'x': [], 'y': []},
            Direction.SOUTH: {'x': [], 'y': []},
            Direction.EAST: {'x': [], 'y': []},
            Direction.WEST: {'x': [], 'y': []},
        }
        self.waiting_time_x = []
        self.waiting_time_num = 0
        self.passed_cars = 0

        self.reward = 0

        self.save = save
        if (save):
            self.f = open("schedule.txt", "w")
        else:
            self.car_schedule = []
            with open('schedule.txt') as fp:
                for line in fp:
                    params = line.split(" ")
                    self.car_schedule.append((params[0], params[1], params[2], params[3]))

    def reset(self):
        self.lanes = {
            Direction.NORTH: Lane('North', Direction.EAST),
            Direction.SOUTH: Lane('South', Direction.WEST),
            Direction.WEST: Lane('West', Direction.NORTH),
            Direction.EAST: Lane('East', Direction.SOUTH)
        }
        self.time = 0
        # 3x3 matrix
        self.occupation_matrix = np.matrix('None,None,None; None,None,None; None,None,None', dtype=Car)
        self.passed_cars = 0
        self.waiting_time_num = 0
        self.waiting_time = []
        self.reward = 0
        return self.get_state()

    def get_state(self):
        state = []
        # give state info about intersection occupation
        for i in range(0,3):
            for j in range(0,3):
                cell = self.occupation_matrix[i,j]
                if (cell == None):
                    state.append(0)
                elif (isinstance(cell, dict)):
                    state.append(0.5)
                else:
                    state.append(1) 
        total_cars = self.lanes[Direction.NORTH].size() + \
                self.lanes[Direction.SOUTH].size() + \
                self.lanes[Direction.WEST].size() + \
                self.lanes[Direction.EAST].size()
        highest_waiting_time = 0
        for key in self.lanes:
            # give state info about how many cars in each lane
            lane = self.lanes[key]
            left_car = lane.peek_left()
            straight_car = lane.peek_straight_right()
            if (left_car != -1 and (self.time - left_car.arrival) > highest_waiting_time):
                highest_waiting_time = (self.time - left_car.arrival)
            if (straight_car != -1 and (self.time - straight_car.arrival) > highest_waiting_time):
                highest_waiting_time = (self.time - straight_car.arrival)
        
        for key in self.lanes:
            # give state info about how many cars in each lane
            lane = self.lanes[key]

            left_car = lane.peek_left()
            if (left_car == -1):
                # no cars and no waiting time
                state.append(-1)
                state.append(-1)
            else:
                state.append(len(lane.left)/total_cars)
                if (highest_waiting_time>0):
                    state.append((self.time-left_car.arrival)/highest_waiting_time)
                else:
                    state.append(-1)

            straight_car = lane.peek_straight_right()
            if (straight_car == -1):
                # no cars and no waiting time
                state.append(-1)
                state.append(-1)
            else:
                state.append(len(lane.straight_right)/total_cars)
                if (highest_waiting_time>0):
                    state.append((self.time-straight_car.arrival)/highest_waiting_time)
                else:
                    state.append(-1)
        return state

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
                car = Car(self.get_random_direction(direction), self.time, self.time_to_move, Direction.WEST)  
            elif (r_number == 1):
                direction = Direction.EAST
                car = Car(self.get_random_direction(direction), self.time, self.time_to_move, Direction.EAST)  
            elif (r_number == 2):
                direction = Direction.SOUTH
                car = Car(self.get_random_direction(direction), self.time, self.time_to_move, Direction.SOUTH)  
            elif (r_number == 3):   
                direction = Direction.NORTH
                car = Car(self.get_random_direction(direction), self.time, self.time_to_move, Direction.NORTH)  

            if (car.destination == self.lanes[direction].left_turn):
                self.lanes[direction].left.append(car)
                if (self.save):
                    self.f.write("{0} {1} {2} {3} \n".format(self.time/self.time_steps_per_hour, 'left', direction, car.destination))
            else:
                self.lanes[direction].straight_right.append(car)
                if (self.save):
                    self.f.write("{0} {1} {2} {3} \n".format(self.time/self.time_steps_per_hour, 'straight', direction, car.destination))

    def add_direction(self, direction):
        car = Car(self.get_random_direction(direction), self.time, self.time_to_move, direction) 
        #print('Added: ' + str(direction) + str(car))  
        if (car.destination == self.lanes[direction].left_turn):
            self.lanes[direction].left.append(car)
        else:
            self.lanes[direction].straight_right.append(car)

    def add_from_to_direction(self, direction_from, direction_to, turn):
        car = Car(direction_to, self.time, self.time_to_move, direction_from)
        if (turn == 'left'):
            self.lanes[direction_from].left.append(car)
        else:
            self.lanes[direction_from].straight_right.append(car)

    def get_random_direction(self, direction_from):
        directions = [Direction.NORTH, Direction.SOUTH, Direction.WEST, Direction.EAST]
        try:
            directions.remove(direction_from)
        except ValueError:
            pass
        return directions[randint(0,2)] 
        
    def green_light(self, direction, lane_type):
        car = None
        if (lane_type == 'left'):
            car = self.lanes[direction].peek_left()
        elif (lane_type == 'straight_right'):
            car = self.lanes[direction].peek_straight_right()

        if (car != None and car != -1):
            allocated = self.allocate_path(direction, car.destination, car)
            if (allocated):
                if (lane_type == 'left'):
                    car = self.lanes[direction].left.pop()
                elif (lane_type == 'straight_right'):
                    car = self.lanes[direction].straight_right.pop()

    def allocate_path(self, direction_from, direction_to, car):
        car_instructions = self.matrix_instructions[direction_from][direction_to]
        empty = True
        count = 0
        for instruction in car_instructions:
            cell = self.occupation_matrix[instruction[0], instruction[1]]
            if (isinstance(cell, dict)):
                if(cell['car'].destination == direction_to and cell['car'].destination_from == direction_from):
                    continue
            elif(isinstance(cell, Car)):
                if (cell.destination_from == direction_from and cell.destination == direction_to and count != 0):
                    continue
            if (cell != None):
                empty = False
            count += 1
        if (empty):
            self.reward += len(car_instructions*150)
            self.waiting_time.append((self.time - car.arrival)/self.time_steps_per_hour*60*60)
            self.waiting_time_dict[direction_to]['y'].append((self.time - car.arrival)/self.time_steps_per_hour*60*60)
            self.waiting_time_dict[direction_to]['x'].append(self.time/self.time_steps_per_hour)
            self.waiting_time_x.append(self.time/self.time_steps_per_hour)
            self.waiting_time_num += (self.time - car.arrival)
            self.passed_cars += 1

            car_copy = car_instructions.copy()
            first = car_copy.pop(0)
            car.directions = car_copy
            self.occupation_matrix[first[0], first[1]] = car
            for instruction in car_copy:
                if (self.occupation_matrix[instruction[0], instruction[1]] == None):
                    self.occupation_matrix[instruction[0], instruction[1]] = {'car': car}
            return True
        else:
            return False

    def make_rect(self, corner, width, height):
        corner2 = corner.clone()
        corner2.move(width, height)
        return Rectangle(corner, corner2)

    def update_occupation_matrix(self):
        box_size = 120
        for i in range(0,3):
            for j in range(0,3):
                car = self.occupation_matrix[i,j]
                
                if (car != None and not(isinstance(car, dict))):
                    # refill the path, might be removed if car in front
                    for path in car.directions:
                        cell = self.occupation_matrix[path[0], path[1]]
                        if (cell == None):
                            self.occupation_matrix[path[0], path[1]] = {'car': car}
                    # move the car
                    moved, direction, moves_left = car.move()
                    if (moved):
                        if (moves_left == 0):
                            self.occupation_matrix[i,j] = None
                        else:
                            self.occupation_matrix[direction[0],direction[1]] = self.occupation_matrix[i,j]
                            self.occupation_matrix[i,j] = None
                if (self.draw):
                    noWest = Text(Point(10, 250), str(self.lanes[Direction.WEST].size()))
                    noNorth = Text(Point(250, 10), str(self.lanes[Direction.NORTH].size()))
                    noEast = Text(Point(475, 250), str(self.lanes[Direction.EAST].size()))
                    nSouth = Text(Point(250, 475), str(self.lanes[Direction.SOUTH].size()))
                    noWest.draw(self.win)
                    obj = self.make_rect(Point(10 , 250), 20, 10)
                    obj.setFill('white')
                    obj.draw(self.win)
                    noNorth.draw(self.win)
                    noEast.draw(self.win)
                    nSouth.draw(self.win)
                    if (car == None):
                        obj = self.make_rect(Point(50 + box_size*j, 50 + box_size*i), box_size, box_size)
                        obj.setFill('white')
                        obj.draw(self.win)
                    elif(isinstance(car, dict)):
                        obj = self.make_rect(Point(50 + box_size*j, 50 + box_size*i), box_size, box_size)
                        obj.setFill('grey')
                        obj.draw(self.win)
                        obj_destination = Text(Point(50 + box_size*j + box_size/2, 50 + box_size*i + box_size/2), str(car['car'].destination))
                        obj_destination.draw(self.win)
                    else:
                        obj = self.make_rect(Point(50 + box_size*j, 50 + box_size*i), box_size, box_size)
                        obj.setFill(car.color)
                        obj.draw(self.win)
                        obj_destination = Text(Point(50 + box_size*j + box_size/2, 50 + box_size*i + box_size/2), str(car.destination))
                        obj_destination.draw(self.win)
        #print(self.occupation_matrix)

    def string_direction_to_enum(self, dir):
        if (dir == 'Direction.NORTH'):
            return Direction.NORTH
        elif (dir == 'Direction.SOUTH'):
            return Direction.SOUTH
        elif (dir == 'Direction.EAST'):
            return Direction.EAST
        elif (dir == 'Direction.WEST'):
            return Direction.WEST

    def training(self):
        for lane in self.lanes:
            for i in range(0,20):
                car = Car(self.get_random_direction(lane), self.time, self.time_to_move, lane) 

                if (car.destination == self.lanes[lane].left_turn):
                    self.lanes[lane].left.append(car)
                else:
                    self.lanes[lane].straight_right.append(car)

    def step(self, action):
        self.update_occupation_matrix()
                
        if (action == 0):
            self.green_light(Direction.NORTH, 'left')
        elif (action == 1):
            self.green_light(Direction.NORTH, 'straight_right')
        elif (action == 2):
            self.green_light(Direction.SOUTH, 'left')
        elif (action == 3):
            self.green_light(Direction.SOUTH, 'straight_right')
        elif (action == 4):
            self.green_light(Direction.WEST, 'left')
        elif (action == 5):
            self.green_light(Direction.WEST, 'straight_right')
        elif (action == 6):
            self.green_light(Direction.EAST, 'left')
        elif (action == 7):
            self.green_light(Direction.EAST, 'straight_right')

        done = True
        for lane in self.lanes:
            lane = self.lanes[lane]
            if (lane.size() != 0):
                done = False

        number_of_cars = self.passed_cars
        if (self.passed_cars == 0):
            number_of_cars = 1

        for key in self.lanes:
            car_left = self.lanes[key].peek_left()
            if (car_left != -1):
                self.reward -= (self.time - car_left.arrival)/(self.time_steps_per_hour/60/60)/100
            car_straight = self.lanes[key].peek_straight_right()
            if (car_straight != -1):
                self.reward -= (self.time-car_straight.arrival)/(self.time_steps_per_hour/60/60)/100

        self.time += 1
        if (self.time >= self.time_steps_per_hour/60*self.minutes):
            #print('waitingin time: ' + str(self.waiting_time_num/number_of_cars))
            return self.get_state(), self.reward, done
        else:
            return self.get_state(), self.reward, done

    def run(self, scheduler):
        if (self.stats):
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
            self.avg_waiting_time = []

        print('day start')
        while (self.time < self.time_steps_per_hour*24):
            self.update_occupation_matrix()
            hour = self.time / self.time_steps_per_hour

            if (self.time % self.car_add_frequency == 0):
                if (self.save):
                    self.stochastic_add(hour)
            
            if (not(self.save)):
                try:
                    car_s = self.car_schedule[0]
                    if (abs(hour - float(car_s[0])) < 0.0001):
                        self.add_from_to_direction(self.string_direction_to_enum(car_s[2]), self.string_direction_to_enum(car_s[3]), car_s[1])
                        self.car_schedule.pop(0)
                except IndexError as e:
                    print(e)

            if (self.draw):
                clear_screen = self.make_rect(Point(70,10), 60, 20)
                clear_screen.setFill('white')
                clear_screen.draw(self.win)
                graphics_hour = Text(Point(100, 20), 'Hour: ' + str(hour.__round__(2)))
                graphics_hour.draw(self.win)

            self.step(scheduler.schedule())

            #self.time -= 1
            if (self.time/self.time_steps_per_hour % 1 == 0):
                print('Simulating hour '  + str(int(self.time/self.time_steps_per_hour)) + '/24')
            if (self.time % self.car_add_frequency == 0 and self.stats):
                #print('here')
                self.save_stats(hour)

            #self.time += 1
        print('day end')
        if (self.save):
            self.f.close()

        if (self.stats):
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
        if (self.passed_cars>0):
            self.avg_waiting_time.append(self.waiting_time)
        else:
            self.avg_waiting_time.append(0)

    def display_stats(self):
        # waiting
        #print('Avg waiting time: ' + str(sum(self.waiting_time)/len(self.waiting_time)))
        # graphs
        color_1 = '--b'
        color_2 = '--g'
        color_3 = 'r'
        plt.subplot(2,1,1)
        combined_total = np.array(list(map(lambda x, y, z, w: x+y+z+w, self.nY_total, self.sY_total, self.eY_total, self.wY_total)))
        combined_left = np.array(list(map(lambda x, y, z, w: x+y+z+w, self.nY_left, self.sY_left, self.eY_left, self.wY_left)))
        combined_straight = np.array(list(map(lambda x, y, z, w: x+y+z+w, self.nY_straight_right,
            self.sY_straight_right, self.eY_straight_right, self.wY_straight_right)))
        plt.plot(self.X, combined_total, color_3,label='Total')
        plt.plot(self.X, combined_left, color_1,label='Left turners')
        plt.plot(self.X, combined_straight, color_2,label='Straight/right turners')
        plt.legend(loc='upper left')
        plt.subplot(2,1,2)
        plt.plot(self.waiting_time_dict[Direction.NORTH]['x'], self.waiting_time_dict[Direction.NORTH]['y'], '.b', label='Average waiting time')
        plt.plot(self.waiting_time_dict[Direction.SOUTH]['x'], self.waiting_time_dict[Direction.SOUTH]['y'], '.g', label='Average waiting time')
        plt.plot(self.waiting_time_dict[Direction.WEST]['x'], self.waiting_time_dict[Direction.WEST]['y'], '.r', label='Average waiting time')
        plt.plot(self.waiting_time_dict[Direction.EAST]['x'], self.waiting_time_dict[Direction.EAST]['y'], '.y', label='Average waiting time')
        plt.show()

class Car:
    def __init__(self, destination, arrival, time_per_square, destination_from):
        self.destination_from = destination_from
        self.destination = destination
        self.arrival = arrival
        self.directions = []
        self.counter = 0
        self.color = color_rgb(randint(0,255), randint(0,255), randint(0,255))
        self.time_per_square = time_per_square

    def move(self):
        if (self.counter >= self.time_per_square):
            if (len(self.directions) == 0):
                self.counter = 0
                return True, None, 0
            else:
                direction = self.directions.pop(0)
                self.counter = 0
                return True, direction, len(self.directions)+1
        self.counter += 1
        return False, None, len(self.directions)
    
    def __str__(self):
        return '[d: ' + str(self.destination) + ' - arr: ' + str(self.arrival) + ']'

    def __repr__(self):
        return str(self.destination)

if __name__ == "__main__":
    simulator = Simulator(1440, stats=True, draw=False, save=True)
    scheduler = DQNScheduler(simulator)
    #simulator.run(scheduler)
    #scheduler = FixedScheduler(simulator.time_steps_per_hour)
    #scheduler = RandomScheduler()
    simulator.run(scheduler)
