from entities import Direction

class LQFScheduler:
    def __init__(self, simulator):
        self.simulator = simulator

    def schedule(self):
        # TODO change rewards
        self.simulator = simulator
        largest_car_amount = 0
        direction = Direction.NONE
        reward = 0

        for key in self.simulator.lanes:
            lane = self.simulator.lanes[key]
            lane_size = lane.size()
            # check if longest queue
            if(largest_car_amount < lane_size):                
                largest_car_amount = lane_size
                direction = key 
        
        success = self.simulator.remove_car(direction, 'left')                
        if (success != -1):
            reward += success**2                    
        success = self.simulator.remove_car(direction, 'straight_left')                
        if (success != -1):
            reward += success**2
        return reward 

    def __str__(self):
        return 'LQF scheduler'
