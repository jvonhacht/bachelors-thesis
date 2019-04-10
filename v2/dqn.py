import time
import random
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

# UN COMMENT FOR TRAINING
from simulator import Simulator

from entities import Direction

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size

        # params
        self.memory = deque(maxlen=10000)
        self.gamma = 0.95
        self.epsilon = 1.0 
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()

        model.add(Dense(20, input_dim=self.state_size, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))

        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        
        for state, action, reward, next_state, done in minibatch:
            target = reward

            if not(done):
                target = reward + self.gamma * np.amax(self.model.predict(next_state)[0])

            target_f = self.model.predict(state)
            target_f[0][action] = target

            self.model.fit(state, target_f, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def act(self, state):
        if (np.random.rand() <= self.epsilon):
            action = random.randint(0,8)
            #print('selecting random: ' + str(action))
            return action
        
        act_values = self.model.predict(state)
        #print('selecting: ' + str(np.argmax(act_values[0])))
        return np.argmax(act_values[0])

    def predict(self, state):
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)

if __name__ == "__main__":
    env = Simulator(10000, traffic='heavy', draw=False)
    agent = DQNAgent(25, 9)
    episodes = 100
    batch_size = 192
    done = False
    env.get_state()

    file = open("save/stats.txt", "w")

    print('Started training...')
    for e in range(episodes+1):
        # new episode, fresh simulation
        state = env.reset()
        state = np.reshape(state, [1, 25])
        time_step = 0
        max_sim_length = 1500
        while(time_step <= max_sim_length):
            # spawn car
            if (time_step % 2 == 0 and time_step <= 750):
                direction = env.get_random_direction("")
                print(direction)
                env.add_direction(direction)

            start = time.time()
            action = agent.act(state)
            next_state, reward, done = env.step(action)
            next_state = np.reshape(next_state, [1, 25])

            agent.remember(state, action, reward, next_state, done)
            state = next_state
            #print('reward: ' +  str(reward))

            if (time_step % 300 == 0):
                pass
                print(state)
                print(env.lanes[Direction.NORTH])
                print(env.lanes[Direction.SOUTH])
                print(env.lanes[Direction.EAST])
                print(env.lanes[Direction.WEST])
                print('timestep: ' + str(time_step))
                print('sim time: ' + str(env.time))
                print(action)
                print('reward: ' + str(reward))
                print('Epsilon: ' + str(agent.epsilon))
                print(env.occupation_matrix)
                file.write(str(time_step) + ' \n')
            # we are done if max sim or no cars left after car spawn stopped
            if time_step == max_sim_length or (done and time_step >= 750):
                # print the score and break out of the loop
                print("episode: {}/{}, score: {}"
                        .format(e, episodes, reward))
                print('cars passed: {0}'.format(env.passed_cars))
                if (env.passed_cars>0):
                    print('Avg waiting time: {0}'.format(env.waiting_time_num/env.passed_cars))
                print('Epsilon: ' + str(agent.epsilon))
                print('---------------------------------------------')
                break
        
            if len(agent.memory) > batch_size:
                agent.replay(batch_size)
            end = time.time()
            time_step += 1
            #print('step' + str(time_step) + ': ' + str(end - start))
        if (e % 10 == 0):
            agent.save("./save/cartpole-dqn.h5")
    file.close()