from logicSim import LogicSimulator
from fifo_scheduler import FifoScheduler
from lqf_scheduler import LQFScheduler
from prio_sn_scheduler import PrioSNScheduler
from prio_we_scheduler import PrioWEScheduler

import numpy as np
import random
import time
import csv

if __name__ == "__main__":
    env = LogicSimulator()
    env.schedulers = schedulers=[FifoScheduler(env),
                                LQFScheduler(env),
                                PrioSNScheduler(env),
                                PrioWEScheduler(env)]
    table = np.zeros((256,len(env.schedulers)))
    episodes = 1000
    epsilon = 1
    epsilon_min = 0.01
    epsilon_decay = 0.99995
    alpha = 0.1
    gamma = 0.9

    with open('action_stats.csv', mode='w') as action_stats:
        action_stats = csv.writer(action_stats, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
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
                #print('state: {0}, next: {1} time: {2}'.format(state, next_state, env.time/env.time_steps_per_hour))
                #print('action: {0} reward: {1}'.format(action, reward))
                # stats
                actions_taken[action] = actions_taken.get(action, 0) + 1
                #rint('reward: {0}'.format(reward))
                #time.sleep(0.5)

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
            csv_data = []
            for key in sorted(actions_taken.keys()):
                print(''.join((str(round(float(actions_taken[key])/float(tot) * 100, 2)), '%')), end=" ")
                csv_data.append(round(float(actions_taken[key])/float(tot) * 100, 2))
            action_stats.writerow(csv_data)
            print()
            print('-----------------------------------')

