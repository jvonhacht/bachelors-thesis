import time
import numpy as np
#import matplotlib
from matplotlib import pyplot as plt
import random
import time
from random import randint
import csv

#from graphics import *

from entities import Direction
from entities import Traffic
from entities import Lane

from fifo_scheduler import FifoScheduler
from fixed_time_scheduler import FixedTimeScheduler
from lqf_scheduler import LQFScheduler
#from dqn_scheduler import DQNScheduler
#from random_scheduler import RandomScheduler
from qtable import QTable

class LogicSimulator:

    # PARAMETERS
    time_steps_per_hour = 18000                    

    def __init__(self, waiting_time_file=None, schedulers=[], action_file=None):       
        # init simulation counter
        self.time = 0

        # initialize lanes
        self.lanes = {
            Direction.NORTH: Lane('North'),
            Direction.SOUTH: Lane('South'),
            Direction.WEST: Lane('West'),
            Direction.EAST: Lane('East')
        }

        self.schedulers = schedulers

        self.north_traffic = 0
        self.south_traffic = 0
        self.west_traffic = 0
        self.east_traffic = 0    
        self.traffic_function = self.fit_curve(plot=False)     

        # controlling schedule delays
        self.time_between_cars = 10
        self.time_between_lane_switch = 45
        self.lane_switch_counter = 0   

        # stats   
        self.removed_cars = 0
        self.summed_waiting_time = 0

        self.x = [] 
        self.ny = []   
        self.wy = []
        self.ey = []
        self.sy = []
        
        self.waiting_data_cars = 0
        self.waiting_data_summed = 0
        self.waiting_data = []
        self.waiting_data_x = []
        self.waiting_time_file = waiting_time_file
        self.action_file = action_file
        #self.action = []                    
                    
    def get_state(self):
        """
        Get the current state of the simulation. Used for dqn training.

        Returns
        -------
        list
            state of the simulation
        """        
        state = 0
        multiplier = [1, 5, 25, 125]
        for index, key in enumerate(self.lanes):
            number_of_cars = self.lanes[key].size()
            if (number_of_cars == 0):
                pass
            elif (number_of_cars > 0 and number_of_cars <= 5):
                state += Traffic.LOW.value * multiplier[index]
            elif (number_of_cars > 5 and number_of_cars <= 12):
                state += Traffic.MEDIUM.value * multiplier[index]
            elif (number_of_cars > 12 and number_of_cars <= 20):
                state += Traffic.HIGH.value * multiplier[index]
            elif (number_of_cars > 20):
                state += Traffic.V_HIGH.value * multiplier[index]
        return state

    def reset(self):
        self.lanes = {
            Direction.NORTH: Lane('North'),
            Direction.SOUTH: Lane('South'),
            Direction.WEST: Lane('West'),
            Direction.EAST: Lane('East')
        }
        self.removed_cars = 0
        self.time = 0
        self.summed_waiting_time = 0
        return self.get_state()

    def reset_queues(self):
        for key in self.lanes:
            self.lanes[key].left.clear()
            self.lanes[key].straight_right.clear()

    def fit_curve(self, plot=False):
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
        if (plot):
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

    def stochastic_add(self, direction):
        """
        Add car to a random lane following traffic probability function.
        Parameters
        ----------
        hour : float
            hour of day
        """
        r_number = random.uniform(0, 1)
        if (r_number <= self.traffic_function(self.time/self.time_steps_per_hour)): 
            self.lanes[direction].passed_cars += 1
            if(randint(0,1) == 0):
                self.lanes[direction].straight_right.append(self.time)
            else:
                self.lanes[direction].left.append(self.time)

    def remove_car(self, direction, lane_type):
        #print('dir: {0} lane> {1}'.format(direction, lane_type))
        self.removed_cars += 1
        self.waiting_data_cars += 1
        car = -1
        try:                
            if (lane_type == 'left'):
                car = self.lanes[direction].left.popleft() 
            elif (lane_type == 'straight_right'):
                car = self.lanes[direction].straight_right.popleft() 
        except:
            return car
        self.summed_waiting_time += self.time - car
        self.waiting_data_summed += (self.time - car)
        return self.time - car

    def step(self, action):
        """
        The step function which updates the simulator to next state.

        Parameters
        ----------
        action: int
            action to perform in this step, a.k.a which lane to turn green

        Returns
        -------
        list
            current state of the simulation
        int
            reward of the action in this state
        bool
            if the simulation is finished or not
        """ 
        reward = 0
        cars = 0  
        switch = False  
        if (self.action_file != None): 
            self.action_file.writerow([self.time/self.time_steps_per_hour, action]) 

        for _ in range(0, 600):
            if (self.time % 100 == 0):
                self.stochastic_add(Direction.NORTH)
                self.stochastic_add(Direction.SOUTH)
                self.stochastic_add(Direction.EAST)
                self.stochastic_add(Direction.WEST)
                
            #print(self.time % self.time_between_cars == 0)
            #print(self.lane_switch_counter)
            if (self.time % self.time_between_cars == 0 and self.lane_switch_counter == 0):
                #print('SHCDULE')
                scheduler_reward, switch, greened_cars = self.schedulers[action].schedule() 
                reward += scheduler_reward
                cars += greened_cars
                if (switch):
                    self.lane_switch_counter = self.time_between_lane_switch
                    switch = False
            
            self.x.append(self.time/self.time_steps_per_hour)
            self.ny.append(self.lanes[Direction.NORTH].size())
            self.sy.append(self.lanes[Direction.SOUTH].size())
            self.wy.append(self.lanes[Direction.WEST].size())
            self.ey.append(self.lanes[Direction.EAST].size())

            #print('-------')

            # lane switch delay
            if(self.lane_switch_counter > 0 and not(switch)):
                self.lane_switch_counter -= 1
            #print('swatch {0}'.format(switch))
            
            #time.sleep(0.1)
            #print('n: {0}, s: {1}, e: {2}, w: {3}'.format(self.lanes[Direction.NORTH].size(),
            #    self.lanes[Direction.SOUTH].size(), self.lanes[Direction.EAST].size(),
            #    self.lanes[Direction.WEST].size()))
            self.time += 1   
        """
        left_waiting_time = 0
        left_cars = 0
        for key in self.lanes:
            for car in self.lanes[key].straight_right:
                left_waiting_time -= 2*(self.time - car)**2
                left_cars += 1
            for car in self.lanes[key].left:
                left_waiting_time -= 2*(self.time - car)**2
                left_cars += 1

        reward += left_waiting_time
        cars += left_cars
        """

        if (cars > 0):
            reward /= cars

        self.waiting_data.append(self.waiting_data_summed/self.time_steps_per_hour/self.waiting_data_cars*60*60)
        self.waiting_data_x.append(self.time/self.time_steps_per_hour)
        if (self.waiting_time_file != None):
            self.waiting_time_file.writerow([self.time/self.time_steps_per_hour, self.waiting_data_summed/self.time_steps_per_hour/self.waiting_data_cars*60*60])
        self.waiting_data_summed = 0
        self.waiting_data_cars = 0

        #print(self.lanes[Direction.NORTH].passed_cars)

        #print('n: {0}, s: {1}, e: {2}, w: {3}'.format(self.lanes[Direction.NORTH].size(),
        #    self.lanes[Direction.SOUTH].size(), self.lanes[Direction.EAST].size(),
        #    self.lanes[Direction.WEST].size()))                   
        
        state = self.get_state()
        #print('state: {0} time: {1}'.format(state, self.time/self.time_steps_per_hour))
        self.lanes[Direction.NORTH].passed_cars = 0
        self.lanes[Direction.SOUTH].passed_cars = 0
        self.lanes[Direction.EAST].passed_cars = 0
        self.lanes[Direction.WEST].passed_cars = 0

        return state, reward, (self.time >= self.time_steps_per_hour*24)


    def get_random_direction(self, dir_from):
        """
        Get a random direction that is not direction_from.

        Parameters
        ----------
        direction_from : Direction
            the direction you want excluded in random
            
        Returns
        -------
        Direction
            the random direction
        """
        dirs = [Direction.NORTH, Direction.SOUTH, Direction.WEST, Direction.EAST]                
        try: 
            dirs.remove(dir_from) 
        except ValueError:
            # Non-valid direction specified
            pass         
        return random.choice(dirs)

    def add_random_car(self):
        direction = self.get_random_direction(Direction.NONE)
        if (randint(0,1) == 1):
            self.lanes[direction].left.append(self.time)
        else:
            self.lanes[direction].straight_right.append(self.time)

    def get_car_amount(self):
        return self.lanes[Direction.NORTH].size() + \
               self.lanes[Direction.SOUTH].size() + \
               self.lanes[Direction.WEST].size()  + \
               self.lanes[Direction.EAST].size()       

    def save_stats(self):
        pass

if __name__ == "__main__":
    scheduler = 5
    with open('waiting_time_{0}.csv'.format(scheduler), mode='w') as waiting_time_file, \
        open('action_selection.csv', mode='w') as action_selection:
        waiting_time_file = csv.writer(waiting_time_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        action_selection = csv.writer(action_selection, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        simulator = LogicSimulator(waiting_time_file=waiting_time_file, action_file=action_selection)
        simulator.schedulers = [
            FifoScheduler(simulator),
            LQFScheduler(simulator),
            FixedTimeScheduler(simulator, 300),
            FixedTimeScheduler(simulator, 200),
            FixedTimeScheduler(simulator, 400),
            #PrioWEScheduler(env)
        ]
        agent = QTable(256, len(simulator.schedulers), simulator.schedulers)
        agent.load_table()
        done = False     
        hour = 1
        state = simulator.get_state()
        while not done:
            state, _, done = simulator.step(agent.act(state, greedy=False))
            #_, _, done = simulator.step(scheduler)
            if (simulator.time % simulator.time_steps_per_hour == 0):
                print('Simulating hour: {0}'.format(hour))
                simulator.save_stats()
                hour += 1
        """
        plt.subplot(4,1,1)
        plt.plot(simulator.x, simulator.ny, 'b',label='NORTH')
        plt.legend(loc='upper left')
        plt.subplot(4,1,2)
        plt.plot(simulator.x, simulator.sy, 'b',label='SOUTH')
        plt.legend(loc='upper left')
        plt.subplot(4,1,3)
        plt.plot(simulator.x, simulator.wy, 'b',label='WEST')
        plt.legend(loc='upper left')
        plt.subplot(4,1,4)
        plt.plot(simulator.x, simulator.ey, 'b',label='EAST')
        plt.legend(loc='upper left')
        """
        plt.plot(simulator.waiting_data_x, simulator.waiting_data, 'o', label='5min avg waiting time', markersize=1)
        plt.legend(loc='upper left')
        plt.show()         

    
    
    
