from entities import Direction

class LQFScheduler:
    def __init__(self, simulator):
        self.simulator = simulator        
        self.previous_direction = Direction.NONE
        self.switch = False

    def schedule(self):         
        self.switch = False     
        direction = Direction.NONE
        cars = 0
        reward = 0
        largest_car_amount = 0

        for key in self.simulator.lanes:
            lane = self.simulator.lanes[key]
            lane_size = lane.size()            
            # check if longest queue
            if(largest_car_amount < lane_size):                
                largest_car_amount = lane_size
                direction = key                 

        success = self.simulator.remove_car(direction, 'left')                
        if (success != -1):
            cars += 1
            reward -= success**2                    
        success = self.simulator.remove_car(direction, 'straight_right')                
        if (success != -1):
            cars += 1
            reward -= success**2                             
        
        self.switch = (self.previous_direction != direction) 
        if (direction == Direction.NONE):
            self.switch = False
        if (direction != Direction.NONE):    
            self.previous_direction = direction
    
        return reward, self.switch, cars 

    def __str__(self):
        return 'LQF scheduler'

    def reset(self):
        self.previous_direction = Direction.NONE
        self.switch = False
