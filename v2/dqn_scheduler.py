
from dqn import DQNAgent
import numpy as np

class DQNScheduler:
    def __init__(self, simulator):
        self.agent = DQNAgent(25,8)
        self.agent.load("./save/cartpole-dqn.h5")
        self.simulator = simulator

    def schedule(self):
        return self.agent.act(np.reshape(self.simulator.get_state(), [1, 25]))
