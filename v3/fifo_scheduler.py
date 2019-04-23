from entities import Direction

class FifoScheduler:
    def __init__(self, simulator):
        self.simulator = simulator
        self.previous_lane = Direction.NONE                

    def schedule(self):
        #self.simulator.remove_car(Direction.NORTH, 'left')
        highest_key = Direction.NONE
        highest_waiting_time = 0
        reward = 0
        cars = 0

        for key in self.simulator.lanes:
            lane = self.simulator.lanes[key]
            lane_waiting_time = 0

            car_left = lane.peek_left()
            if (car_left != -1):
                lane_waiting_time += self.simulator.time - car_left
            car_straight = lane.peek_straight_right()
            if (car_straight != -1):
                lane_waiting_time += self.simulator.time - car_straight
            
            if (lane_waiting_time > highest_waiting_time):
                highest_waiting_time = lane_waiting_time
                highest_key = key
        # return reward: -(squared waiting time)        
        success = self.simulator.remove_car(highest_key, 'left') 
        if (success != -1):
            reward -= success**2
            cars += 1
        success = self.simulator.remove_car(highest_key, 'straight_right')
        if (success != -1):
            cars += 1
            reward -= success**2        
        
        # switch previous lane of lane switch
        switch = (self.previous_lane != highest_key) 
        if (highest_key == Direction.NONE):
            switch = False
        if (highest_key != Direction.NONE):    
            self.previous_lane = highest_key
        return reward, switch, cars

    def __str__(self):
        return 'Fifo scheduler'
