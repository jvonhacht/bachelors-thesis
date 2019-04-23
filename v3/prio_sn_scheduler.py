from entities import Direction
import random

class PrioSNScheduler:
    def __init__(self, simulator):
        self.simulator = simulator

    def schedule(self):
        # TODO change rewards
        prio_prob = 1.0        
        reward = 0      
        cars = 0  

        # choose either north or south lane
        if (self.simulator.lanes[Direction.NORTH].size() + self.simulator.lanes[Direction.SOUTH].size() > 0):                
            # north lane            
            success = self.simulator.remove_car(Direction.NORTH, 'left')                
            if (success != -1):                                
                cars += 1
                reward -= success**2                     
            success = self.simulator.remove_car(Direction.NORTH, 'straight_right')                
            if (success != -1):                    
                cars += 1
                reward -= success**2                                         
            # south lane        
            success = self.simulator.remove_car(Direction.SOUTH, 'left')                
            if (success != -1):
                cars += 1
                reward -= success**2                 
            success = self.simulator.remove_car(Direction.SOUTH, 'straight_right')                
            if (success != -1):
                cars += 1
                reward -= success**2             
            return reward, False, cars    
         
        lane = random.randint(0,1)
        # west lane
        if(lane == 0):
            success = self.simulator.remove_car(Direction.WEST, 'left')                
            if (success != -1):
                cars += 1
                reward -= success**2                 
            success = self.simulator.remove_car(Direction.WEST, 'straight_right')                
            if (success != -1):
                cars += 1
                reward -= success**2                
            return reward, False, cars  
        # east lane
        else:
            success = self.simulator.remove_car(Direction.EAST, 'left')                
            if (success != -1):
                cars += 1
                reward -= success**2                 
            success = self.simulator.remove_car(Direction.EAST, 'straight_right')                
            if (success != -1):
                cars += 1
                reward -= success**2             
            return reward, False, cars          
    
    def __str__(self):
        return 'Prioritise SOUTH/NORTH scheduler'
