#from logicSim import LogicSimulator

from fifo_scheduler import FifoScheduler
from lqf_scheduler import LQFScheduler
from prio_sn_scheduler import PrioSNScheduler
from prio_we_scheduler import PrioWEScheduler
from fixed_time_scheduler import FixedTimeScheduler

import numpy as np
import random
import time
import csv
from entities import Direction

class QTable:
    def __init__(self, height, width, action_space):
        self.episodes = 1000
        self.epsilon = 1
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9995
        self.alpha = 0.05
        self.gamma = 0.9
        self.action_space = action_space

        self.table = np.zeros((height, width))
        self.table_b = np.zeros((height, width))

    def save_table(self):
        np.savetxt('table_a.txt', self.table, fmt='%d')
        np.savetxt('table_b.txt', self.table_b, fmt='%d')

    def load_table(self):
        try:
            self.table = np.loadtxt('table_a.txt', dtype=int)
            self.table_b = np.loadtxt('table_b.txt', dtype=int)
        except OSError:
            pass

    def act(self, state, greedy=True):
        # epsilon greedy
        if (random.uniform(0, 1) < self.epsilon):
            return random.randint(0,len(self.action_space)-1)
        else:
            return np.argmax(self.table[state])

if __name__ == "__main__":
    env = LogicSimulator()
    env.schedulers = schedulers=[
        FifoScheduler(env),
        LQFScheduler(env),
        FixedTimeScheduler(env, 300),
        FixedTimeScheduler(env, 100),
        FixedTimeScheduler(env, 500),
        #PrioWEScheduler(env)
    ]
    qtable = QTable(256, len(env.schedulers), env.schedulers)

    with open('action_stats.csv', mode='w') as action_stats:
        with open('waiting_times.csv', mode='w') as waiting_times:
            action_stats = csv.writer(action_stats, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            waiting_times = csv.writer(waiting_times, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            previous_states = {}
            for e in range(0, qtable.episodes+1):
                state = env.reset()
                actions_taken = {}
                for i in range(0, len(env.schedulers)):
                    actions_taken[i] = 0
                done = False
                #print(actions_taken)

                while not done:
                    action = qtable.act(state)
                    next_state, reward, done = env.step(action)
                    #print('state: {0}, next: {1} time: {2}'.format(state, next_state, env.time/env.time_steps_per_hour))
                    #print('action: {0} reward: {1}'.format(action, reward))
                    # stats
                    previous_states[state] = previous_states.get(state, 0) + 1
                    actions_taken[action] += 1
                    if (random.randint(0,1) == 0):
                        old_value = qtable.table[state, action]
                        next_max = np.argmax(qtable.table[next_state])
                        #print(state)

                        # Update the new value
                        new_value = (1 - qtable.alpha) * old_value + qtable.alpha * \
                            (reward + qtable.gamma * qtable.table_b[next_state, next_max] - old_value)
                        #print('state: {0} action: {1}'.format(state, action))
                        qtable.table[state, action] = new_value
                    else:
                        old_value = qtable.table_b[state, action]
                        next_max = np.argmax(qtable.table_b[next_state])
                        #print(state)

                        # Update the new value
                        new_value = (1 - qtable.alpha) * old_value + qtable.alpha * \
                            (reward + qtable.gamma * qtable.table[next_state, next_max] - old_value)
                        #print('state: {0} action: {1}'.format(state, action))
                        qtable.table_b[state, action] = new_value
                    state = next_state
                    #env.reset_queues()

                    if (qtable.epsilon > qtable.epsilon_min):
                        qtable.epsilon *= qtable.epsilon_decay
                qtable.save_table()
                print('Episode {0}/{1} epsilon: {2}'.format(e, qtable.episodes, qtable.epsilon))
                #print(len(previous_states.keys()))
                #print(previous_states[255])
                #print(table)
                tot = sum(actions_taken.values())
                csv_data = []
                for key in sorted(actions_taken.keys()):
                    print(''.join((str(round(float(actions_taken[key])/float(tot) * 100, 2)), '%')), end=" ")
                    csv_data.append(round(float(actions_taken[key])/float(tot) * 100, 2))
                action_stats.writerow(csv_data)
                waiting_times.writerow([str(round(env.summed_waiting_time/env.removed_cars, 4))])
                print()
                print('-----------------------------------')

