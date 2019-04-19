import time
#import numpy as np
#import matplotlib
#from matplotlib import pyplot as plt
import random
import copy
from random import randint

#from graphics import *

from entities import Direction
from entities import Lane

#from fixed_scheduler import FixedScheduler
#from dqn_scheduler import DQNScheduler
#from random_scheduler import RandomScheduler

class LogicSimulator:

    # PARAMETERS
    time_steps_per_hour = 18000                    

    def __init__(self):       
        # init simulation counter
        self.time = 0

        # initialize lanes
        self.lanes = {
            Direction.NORTH: Lane('North'),
            Direction.SOUTH: Lane('South'),
            Direction.WEST: Lane('West'),
            Direction.EAST: Lane('East')
        }
        
        # fill lanes with cars
        """
        for i in range(0, 100):  
            direction = self.get_random_direction(Direction.NONE)  
            if(randint(0, 1) == 1):
                self.lanes[direction].straight_right.append(0)                    
            else:            
                self.lanes[direction].left.append(0)  
        """                              
                    
    def get_state(self):
        """
        Get the current state of the simulation. Used for dqn training.

        Returns
        -------
        list
            state of the simulation as NN input
        """        
        state = []
        lane_sizes = []
        total_count = 0

        # get car amount of lanes
        for lane in self.lanes:
            lane_sizes.append(len(self.lanes[lane].left))
            lane_sizes.append(len(self.lanes[lane].straight_right))  
            total_count += self.lanes[lane].size()                     
        
        if (total_count == 0):
            total_count = 1

        # calculate car amount in each lane 
        # relative to maximum lane size
        for lane in lane_sizes:            
            state.append(float(lane)/total_count)
        
        # list of total waiting 
        # time for each lane
        wait_size = []
        total_wait = 0

        # get total waiting time for each lane
        for lane in self.lanes:        
            if(self.lanes[lane].peek_straight_right() != -1):
                wait_size.append(self.time - self.lanes[lane].peek_straight_right())
                total_wait += self.time - self.lanes[lane].peek_straight_right()
            else:
                wait_size.append(0)
            if(self.lanes[lane].peek_left() != -1):
                wait_size.append(self.time - self.lanes[lane].peek_left())   
                total_wait += self.time - self.lanes[lane].peek_left()         
            else:
                wait_size.append(0)
        
        if (total_wait == 0):
            total_wait = 1

        # calculate relative waiting 
        # time for each lane
        for wait_time in wait_size:            
            state.append(float(wait_time)/total_wait)
       
        return state

    def reset(self):
        self.lanes = {
            Direction.NORTH: Lane('North'),
            Direction.SOUTH: Lane('South'),
            Direction.WEST: Lane('West'),
            Direction.EAST: Lane('East')
        }
        self.time = 0
        return self.get_state()

    def remove_car(self, direction, lane_type):
        try:                
            if (lane_type == 'left'):
                self.lanes[direction].left.popleft() 
            elif (lane_type == 'straight_right'):
                self.lanes[direction].straight_right.popleft() 
        except:
            return False
        return True

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

        success = False
        greened_lanes = [(Direction.NONE, ""), (Direction.NONE, "")]

        if (action == 0):
            north_success = self.remove_car(Direction.NORTH, 'straight_right')
            south_success = self.remove_car(Direction.SOUTH, 'straight_right')
            success = north_success or south_success                        
            greened_lanes.append((Direction.NORTH, 'straight_right'))
            greened_lanes.append((Direction.SOUTH, 'straight_right'))
        elif (action == 1):  
            west_success = self.remove_car(Direction.WEST, 'straight_right')
            east_success = self.remove_car(Direction.EAST, 'straight_right')
            success = west_success or east_success
            greened_lanes.append((Direction.WEST, 'straight_right'))
            greened_lanes.append((Direction.EAST, 'straight_right'))
        elif (action == 2):
            left_success = self.remove_car(Direction.NORTH, 'left')
            straight_success = self.remove_car(Direction.NORTH, 'straight_right')
            success = left_success or straight_success
            greened_lanes.append((Direction.NORTH, 'straight_right'))
            greened_lanes.append((Direction.NORTH, 'left'))
        elif (action == 3):
            left_success = self.remove_car(Direction.SOUTH, 'left')
            straight_success = self.remove_car(Direction.SOUTH, 'straight_right')
            success = left_success or straight_success
            greened_lanes.append((Direction.SOUTH, 'straight_right'))
            greened_lanes.append((Direction.SOUTH, 'left'))
        elif (action == 4):
            left_success = self.remove_car(Direction.WEST, 'left')
            straight_success = self.remove_car(Direction.WEST, 'straight_right')
            success = left_success or straight_success
            greened_lanes.append((Direction.WEST, 'straight_right'))
            greened_lanes.append((Direction.WEST, 'left'))
        elif (action == 5):
            left_success = self.remove_car(Direction.EAST, 'left')
            straight_success = self.remove_car(Direction.EAST, 'straight_right')
            success = left_success or straight_success
            greened_lanes.append((Direction.EAST, 'straight_right'))
            greened_lanes.append((Direction.EAST, 'left'))        

        # basic reward if green light
        if (success):
            reward = 1    

        # negative reward for waiting cars
        for key in self.lanes:
            # not Direction.X and not 'left'
            car_left = self.lanes[key].peek_left()
            if (not(car_left == -1) and not(key == greened_lanes[0][0] and 'left' == greened_lanes[0][1])):
                reward -= (self.time - car_left) / 6000

            # not Direction.X and not 'straight'
            car_straight = self.lanes[key].peek_straight_right()
            if (not(car_straight == -1) and not(key == greened_lanes[1][0] and 'straight_right' == greened_lanes[1][1])):
                reward -= (self.time - car_straight) / 6000

        # check if simulation done
        done = False if self.get_car_amount() != 0 else True      
        
        self.time += 1
        return self.get_state(), reward, done


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

if __name__ == "__main__":
    simulator = LogicSimulator()      

    done = False
    while not done:
        done = simulator.step(randint(0,6))[2]              

    for i in range(1,5): 
        pass

    
    
    
