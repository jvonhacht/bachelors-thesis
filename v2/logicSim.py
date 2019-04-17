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

if __name__ == "__main__":
    simulator = LogicSimulator(1440)        
    
    
