import time
import random
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

# UN COMMENT FOR TRAINING
#from simulator import Simulator

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size

        # params
        self.memory = deque(maxlen=10000)
        self.gamma = 0.95   
        self.epsilon = 1.0 
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()

        model.add(Dense(75, input_dim=self.state_size, activation='relu'))
        model.add(Dense(50, activation='relu'))
        #model.add(Dense(50, activation='relu'))
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
            return random.randint(0,7)
        
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)

if __name__ == "__main__":
    env = Simulator(1, traffic='heavy', draw=False)
    agent = DQNAgent(25, 8)
    episodes = 1000
    batch_size = 32
    done = False

    for e in range(episodes):
        # new episode, fresh simulation
        state = env.reset()
        state = np.reshape(state, [1, 25])

        for time_step in range(int(env.time_steps_per_hour/60*5)):
            start = time.time()
            action = agent.act(state)
            #print(action)
            next_state, reward, done = env.step(action)
            #print('reward: ' + str(reward))
            next_state = np.reshape(next_state, [1, 25])

            agent.remember(state, action, reward, next_state, done)
            state = next_state

            if (time_step % 100 == 0):
                print('timestep: ' + str(time_step))

            if done:
                # print the score and break out of the loop
                print("episode: {}/{}, score: {}"
                        .format(e, episodes, reward))
                print('cars passed: {0}'.format(env.passed_cars))
                print('Avg waiting time: {0}'.format(env.waiting_time_num/env.passed_cars))
                break
        
            if len(agent.memory) > batch_size:
                agent.replay(batch_size)
            end = time.time()
            #print('step' + str(time_step) + ': ' + str(end - start))
        if (e % 10 == 0):
            agent.save("./save/cartpole-dqn.h5")