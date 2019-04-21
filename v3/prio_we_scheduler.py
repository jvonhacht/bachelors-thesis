from entities import Direction
import random

class PrioWEScheduler:
    def __init__(self, simulator):
        self.simulator = simulator

    def schedule(self):
<<<<<<< HEAD
        return 1
=======
        # TODO change rewards
        prio_prob = 1.0        
        reward = 0        
>>>>>>> 62d28221ab027038634b753904b525115b00b20e

        # choose either west or east lane
        if (random.uniform(0,1) <= prio_prob):                
            # west lane                            
            success = self.simulator.remove_car(Direction.WEST, 'left')                
            if (success != -1):
                reward -= success**2                 
            success = self.simulator.remove_car(Direction.WEST, 'straight_left')                
            if (success != -1):                    
                reward -= success**2                              
            # east lane            
            success = self.simulator.remove_car(Direction.EAST, 'left')                
            if (success != -1):
                reward -= success**2                 
            success = self.simulator.remove_car(Direction.EAST, 'straight_left')                
            if (success != -1):
                reward -= success**2             
            return reward     
         
        lane = random.randint(0,1)
        # nort lane
        if(lane == 0):
            success = self.simulator.remove_car(Direction.NORTH, 'left')                
            if (success != -1):
                reward -= success**2             
            success = self.simulator.remove_car(Direction.NORTH, 'straight_left')                
            if (success != -1):
                reward -= success**2             
            return reward      
        # south lane
        else:
            success = self.simulator.remove_car(Direction.SOUTH, 'left')                
            if (success != -1):
                reward -= success**2                 
            success = self.simulator.remove_car(Direction.SOUTH, 'straight_left')                
            if (success != -1):
                reward -= success**2             
            return reward           
    
    def __str__(self):
        return 'Prioritise WEST/EAST scheduler'
