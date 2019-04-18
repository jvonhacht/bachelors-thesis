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
        # initialize lanes
        self.lanes = {
            Direction.NORTH: Lane('North', Direction.EAST),
            Direction.SOUTH: Lane('South', Direction.WEST),
            Direction.WEST: Lane('West', Direction.NORTH),
            Direction.EAST: Lane('East', Direction.SOUTH)
        }
        
        # fill lanes with cars
        for _ in range(0, 100):  
            direction = self.get_random_direction(Direction.NONE)  
            if(randint(0,2) == 1):
                self.lanes[direction].straight_right.append(Car(self.get_random_direction(direction), direction))                    
            else:            
                self.lanes[direction].left.append(Car(self.get_random_direction(direction), direction))                                
                    
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

        # get car amount of lanes
        for lane in self.lanes:
            lane_sizes.append(self.lanes[lane].size())
        
        # amount of car in max lane
        max_amount = max(lane_sizes) 
                        
        if(max_amount != 0):
            # calculate car amount in each lane 
            # relative to maximum lane size
            for i in range(0, 4):            
                state.append(float(lane_sizes[i])/max_amount)
        
        print(state)
        return state

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
        if (action == 0):
            north_success = self.remove_car(Direction.NORTH, 'straight_right')
            south_success = self.remove_car(Direction.SOUTH, 'straight_right')
            success = north_success or south_success
        elif (action == 1):  
            west_success = self.remove_car(Direction.WEST, 'straight_right')
            east_success = self.remove_car(Direction.EAST, 'straight_right')
            success = west_success or east_success
        elif (action == 2):
            left_success = self.remove_car(Direction.NORTH, 'left')
            straight_success = self.remove_car(Direction.NORTH, 'straight_right')
            success = left_success or straight_success
        elif (action == 3):
            left_success = self.remove_car(Direction.SOUTH, 'left')
            straight_success = self.remove_car(Direction.SOUTH, 'straight_right')
            success = left_success or straight_success
        elif (action == 4):
            left_success = self.remove_car(Direction.WEST, 'left')
            straight_success = self.remove_car(Direction.WEST, 'straight_right')
            success = left_success or straight_success
        elif (action == 5):
            left_success = self.remove_car(Direction.EAST, 'left')
            straight_success = self.remove_car(Direction.EAST, 'straight_right')
            success = left_success or straight_success

        # basic reward if green light
        if (success):
            reward = 1

        done = False if self.get_car_amount() != 0 else True      
        
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

    def get_car_amount(self):
        return self.lanes[Direction.NORTH].size() + \
               self.lanes[Direction.SOUTH].size() + \
               self.lanes[Direction.WEST].size()  + \
               self.lanes[Direction.EAST].size()

class Car:
    def __init__(self, destination, destination_from):
        self.destination = destination
        self.destination_from = destination_from                

if __name__ == "__main__":
    simulator = LogicSimulator()      
    for i in range(1,5):
        print(simulator.lanes[i].size())
    simulator.get_state()

    done = False
    while not done:
        done = simulator.step(randint(0,3))[2]              

    for i in range(1,5):
        print(simulator.lanes[i].size())    

    
    
    
