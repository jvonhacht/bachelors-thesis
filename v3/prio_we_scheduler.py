from entities import Direction
import random

class PrioWEScheduler:
    def __init__(self, simulator):
        self.simulator = simulator

    def schedule(self):
        # TODO change rewards
        prio_prob = 1.0        
        reward = 0        

        # choose either west or east lane
        if (random.uniform(0,1) <= prio_prob):                
            # west lane                            
            success = self.simulator.remove_car(Direction.WEST, 'left')                
            if (success != -1):
                reward += success                    
            success = self.simulator.remove_car(Direction.WEST, 'straight_left')                
            if (success != -1):                    
                reward += success                                            
            # east lane            
            success = self.simulator.remove_car(Direction.EAST, 'left')                
            if (success != -1):
                reward += success                    
            success = self.simulator.remove_car(Direction.EAST, 'straight_left')                
            if (success != -1):
                reward += success                
            return reward     
         
        lane = random.randint(0,1)
        # nort lane
        if(lane == 0):
            success = self.simulator.remove_car(Direction.NORTH, 'left')                
            if (success != -1):
                reward += success                    
            success = self.simulator.remove_car(Direction.NORTH, 'straight_left')                
            if (success != -1):
                reward += success                
            return reward      
        # south lane
        else:
            success = self.simulator.remove_car(Direction.SOUTH, 'left')                
            if (success != -1):
                reward += success                    
            success = self.simulator.remove_car(Direction.SOUTH, 'straight_left')                
            if (success != -1):
                reward += success                
            return reward           
    
    def __str__(self):
        return 'Prioritise WEST/EAST scheduler'
