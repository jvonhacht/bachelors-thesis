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

        if (action == 0):
            try:                
                self.lanes[Direction.NORTH].straight_right.popleft()                        
            except:
                pass
            try:                            
                self.lanes[Direction.NORTH].left.popleft() 
            except:
                pass
        elif (action == 1):  
            try:
                self.lanes[Direction.SOUTH].straight_right.popleft()         
            except:
                pass
            try:
                self.lanes[Direction.SOUTH].left.popleft()                              
            except:
                pass
        elif (action == 2):
            try:
                self.lanes[Direction.WEST].straight_right.popleft()         
            except:
                pass
            try:
                self.lanes[Direction.WEST].left.popleft()         
            except:
                pass
        elif (action == 3):
            try:
                self.lanes[Direction.EAST].straight_right.popleft()         
            except:
                pass
            try:
                self.lanes[Direction.EAST].left.popleft()        
            except:
                pass

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

    
    
    
