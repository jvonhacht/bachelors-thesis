
from dqn import DQNAgent
import numpy as np

class DQNScheduler:
    def __init__(self, simulator):
        self.agent = DQNAgent(17,9)
        self.agent.load("./save/cartpole-dqn.h5")
        self.simulator = simulator
        self.agent.epsilon = 0

    def schedule(self):
        action = self.agent.act(np.reshape(self.simulator.get_state(), [1, 17]))
        return action
