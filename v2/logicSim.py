import time
#import numpy as np
#import matplotlib
#matplotlib.use("TkAgg")
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

    def __init__(self, minutes, traffic='stochastic'):                      
        # simulation runtime
        self.minutes = minutes

        # initialize lanes
        self.lanes = {
            Direction.NORTH: Lane('North', Direction.EAST),
            Direction.SOUTH: Lane('South', Direction.WEST),
            Direction.WEST: Lane('West', Direction.NORTH),
            Direction.EAST: Lane('East', Direction.SOUTH)
        }
        
        # fill lanes with cars
        for i in range(1, 20):  
            direction = self.get_random_direction(None)                       
            self.lanes[direction].straight_right.append(Car(self.get_random_direction(direction), direction))        
                    
    def get_state(self):
        """
        Get the current state of the simulation. Used for dqn training.

        Returns
        -------
        list
            state of the simulation as NN input
        """        

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

class Car:
    def __init__(self, destination, destination_from):
        self.destination = destination
        self.destination_from = destination_from                

if __name__ == "__main__":
    simulator = LogicSimulator(1440)      
    for i in range(1,5):
        print(simulator.lanes[i].size())

    
    
    
