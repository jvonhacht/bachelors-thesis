from logicSim import LogicSimulator
from fifo_scheduler import FifoScheduler
from lqf_scheduler import LQFScheduler
from prio_sn_scheduler import PrioSNScheduler
from prio_we_scheduler import PrioWEScheduler

import numpy as np
import random
import time

if __name__ == "__main__":
    env = LogicSimulator()
    env.schedulers = schedulers=[FifoScheduler(env),
                                LQFScheduler(env),
                                PrioSNScheduler(env),
                                PrioWEScheduler(env)]
    table = np.zeros((256,len(env.schedulers)))
    episodes = 1000
    epsilon = 1
    epsilon_min = 0.1
    epsilon_decay = 0.9995
    alpha = 0.1
    gamma = 0.9

    for e in range(0, episodes):
        state = env.reset()
        actions_taken = {}
        done = False

        while not done:
            # epsilon greedy
            if random.uniform(0, 1) < epsilon:
                action = random.randint(0,len(env.schedulers)-1)
            else:
                action = np.argmax(table[state])
            next_state, reward, done = env.step(action)
            actions_taken[action] = actions_taken.get(action, 0) + 1
            #rint('reward: {0}'.format(reward))

            old_value = table[state, action]
            next_max = np.max(table[next_state])

            # Update the new value
            new_value = (1 - alpha) * old_value + alpha * \
                (reward + gamma * next_max)
            #print('state: {0} action: {1}'.format(state, action))
            table[state, action] = new_value
            state = next_state

            if (epsilon > epsilon_min):
                epsilon *= epsilon_decay
        print('Episode {0}/{1} epsilon: {2}'.format(e, episodes, epsilon))
        print(table)
        tot = sum(actions_taken.values())
        for key in actions_taken:
            print(''.join((str(round(float(actions_taken[key])/float(tot) * 100, 2)), '%')), end=" ")
        print()
        print('-----------------------------------')

