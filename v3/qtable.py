from logicSim import LogicSimulator
from fifo_scheduler import FifoScheduler

import numpy as np
import random
import time

if __name__ == "__main__":
    env = LogicSimulator()
    env.schedulers = schedulers=[FifoScheduler(env)]
    table = np.zeros((256,len(env.schedulers)))
    episodes = 1000
    epsilon = 0.1
    alpha = 0.1
    gamma = 0.95

    for e in range(0, episodes):
        state = env.reset()
        done = False

        while not done:
            # epsilon greedy
            if random.uniform(0, 1) < epsilon:
                action = random.randint(0,len(env.schedulers)-1)
            else:
                action = np.argmax(table[state])
            next_state, reward, done = env.step(action)
            #rint('reward: {0}'.format(reward))

            old_value = table[state, action]
            next_max = np.max(table[next_state])

            # Update the new value
            new_value = (1 - alpha) * old_value + alpha * \
                (reward + gamma * next_max)
            print('state: {0} action: {1}'.format(state, action))
            table[state, action] = new_value
            state = next_state
        print('Episode {0}/{1}'.format(e, episodes))
        print(table)
        print('-----------------------------------')

