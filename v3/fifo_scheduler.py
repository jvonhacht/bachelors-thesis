from entities import Direction

class FifoScheduler:
    def __init__(self, simulator):
        self.simulator = simulator

    def schedule(self):
        """
        self.simulator.remove_car(Direction.NORTH, 'left')
        highest_key = Direction.NONE
        highest_waiting_time = 0
        for key in self.simulator.lanes:
            lane = self.simulator.lanes[key]
            lane_waiting_time = 0

            car_left = lane.peek_left()
            if (car_left != -1):
                lane_waiting_time += car_left
            car_straight = lane.peek_straight_right()
            if (car_straight != -1):
                lane_waiting_time += car_straight
            
            if (lane_waiting_time > highest_waiting_time):
                highest_waiting_time = lane_waiting_time
                highest_key = key
        # return reward: -(squared waiting time)
        reward = 0
        success = self.simulator.remove_car(highest_key, 'left')
        if (success != -1):
            reward -= success**2
        success = self.simulator.remove_car(highest_key, 'straight_right')
        if (success != -1):
            reward -= success**2
        """
        reward = -1000
        return reward

    def __str__(self):
        return 'Fifo scheduler'
