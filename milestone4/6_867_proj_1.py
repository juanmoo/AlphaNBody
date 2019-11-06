# -*- coding: utf-8 -*-
"""6.867_proj_1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xbrT3YdzlHNKphy87dOtwd_59FpMWPsF

Putting code from https://adventuresinmachinelearning.com/reinforcement-learning-tensorflow/ on notebook
"""

!pip install tensorflow
!pip install gym

import gym
import numpy as np
import tensorflow as tf
import matplotlib.pylab as plt
import random
import math
from numpy import linalg as LA
import copy

MAX_EPSILON = 1
MIN_EPSILON = 0.01
LAMBDA = 0.0001
GAMMA = 0.99
BATCH_SIZE = 50

"""Our code"""

class Particle(object):
    default_fuel = 100

    def __init__(self,
                 id,
                 mass,
                 initial_time=0,
                 initial_position=None,
                 initial_velocity=None,
                 initial_fuel=default_fuel,
                 exhaust_velocity = None):

        self.id = id  # Particle's UID
        self.mass = mass  # Particle's mass in kilograms
        self.exhaust_velocity = exhaust_velocity
        if initial_position is None:
            initial_position = np.zeros((2, 1))

        if initial_velocity is None:
            initial_velocity = np.zeros((2, 1))
            
        if self.exhaust_velocity is None:
            self.exhaust_velocity = 0

        '''
        List of instantaneous particle states. Each particle state is a tuple
        with the following structure: (time, location, velocity, fuel_weight)
        The dimensions of each of the entries in the tuple are as follows:
        time -> seconds
        location -> n-dimensional numpy vector - meters^2
        velocity -> n-dimensional numpy vector - (meters/second)^2
        fuel_weight -> scalar - kilograms
       '''
        self.state_list = [
            (initial_time, initial_position, initial_velocity, initial_fuel)
        ]

    def current_position(self):
        return self.state_list[-1][1]

    def current_state(self):
        return self.state_list[-1][1:]

    def step(self, update_function, thrust, step_length):
        new_state = update_function(self, thrust, step_length)
        self.state_list.append(new_state)
        reward = self.get_reward()
        done = self.is_done()
        log = "TODO add logging"
        return new_state, reward, done, log

    def is_done(self):
        return False

    def get_reward(self):
        return -1


class Scene(object):
    def __init__(self, particle_list, update_functions, step_length, target, global_start_time=0):
        self.init_particles = particle_list

        self.particle_list = copy.deepcopy(particle_list)

        self.ship = self.particle_list[0]

        self.target = target

        # How each of the particles' position is to be updated
        self.update_functions = update_functions
        self.step_length = step_length

        #params
        self.action_list = [(0, 0), (1, 0), (1, np.pi), (1, np.pi/2), (1, np.pi * 3 / 2)]
        self.max_steps = 200
        self.steps_taken = 0
        self.goal_dist = .1

    def reset(self):
        self.steps_taken = 0
        self.particle_list = copy.deepcopy(self.init_particles)
        self.ship = self.particle_list[0]
        return self.get_next_state()

    def get_positions(self):
        return [tuple(p.current_position().flatten()) for p in self.particle_list]

    def old_step(self, input_thrusts):
        for (particle, update_function, thrust) in \
                zip(self.particle_list, self.update_functions, input_thrusts):

            particle.step(update_function, thrust, self.step_length)
        self.steps_taken += 1
        reward = self.get_reward()
        done = self.is_done()
        log = "TODO do log"
        return self.get_positions(), reward, done, log

    def step(self, action):
      #action is a number 0-4
      # 0 - do nothing
      # 1/2 -  +/- x
      # 3/4 -  +/- y
      input_thrusts = [(0,0) for x in range(len(self.particle_list))]
      input_thrusts[0] = self.action_list[action]
      for (particle, update_function, thrust) in \
                zip(self.particle_list, self.update_functions, input_thrusts):

            particle.step(update_function, thrust, self.step_length)
      self.steps_taken += 1
      next_step = self.get_next_state()
      reward = self.get_reward()
      done = self.is_done()
      log = "TODO do log"
      
      return next_step, reward, done, log


    def get_next_state(self):
        current_state = self.ship.current_state()
        return np.array([current_state[0][0], current_state[0][1], current_state[1][0], current_state[1][1], current_state[2]])

    def is_done(self):
        return LA.norm(self.target - self.ship.current_position()) < self.goal_dist or self.max_steps <= self.steps_taken


    def get_distance_to_goal(self):
        return LA.norm(self.target - self.ship.current_position())

    def get_reward(self):
        distance = self.get_distance_to_goal()
        if distance < self.goal_dist:
            reward = 10000
        elif distance < .5:
            reward = 20
        elif distance < 1:
            reward = 10
        else:
            reward = 0
        return reward - 1

K = 9.81


def zero_update_function(particle, thrust, step_length):
    state = list(particle.state_list[-1])
    state[0] += step_length
    return tuple(state)


def gravitaional_pull_from_list(particle_list):
    def update_function(particle, thrust, step_length):
        net_f = np.zeros((2, 1))
        time, position, velocity, fuel = particle.state_list[-1]
        m0 = (fuel + particle.mass)
        for p in particle_list:
            if p.id != particle.id:
                distance_p = position - p.current_position()
                force_p = - ((K * m0 * p.mass)/(LA.norm(distance_p)
                                                           ** 2)) * (distance_p/LA.norm(distance_p))
                net_f += force_p

        # Add Thrust Logic Here #
        mag_thrust, dir_thrust = thrust
        
        if mag_thrust > fuel:
            mag_thrust = fuel
        dv_thrust = particle.exhaust_velocity*np.log(m0/(m0 - mag_thrust))
        
        dv_thrust = np.array([dv_thrust* np.cos(dir_thrust), dv_thrust* np.sin(dir_thrust)]).reshape((2,1))
        #########################
        net_a = net_f/m0
        dv = net_a * step_length
        avg_v = velocity + .5 * dv + dv_thrust
        next_time = time + step_length
        next_position = position + avg_v * step_length
        next_velocity = velocity + dv + dv_thrust
        next_fuel = fuel - mag_thrust

        return (next_time, next_position, next_velocity, next_fuel)
    return update_function

p1_position = np.array([-10, 0]).reshape((2, 1))
p1_velocity = np.array([0, 2]).reshape((2, 1))
p1 = Particle(1, 10, initial_position=p1_position,
              initial_velocity=p1_velocity)


p2_position = np.array([10, 0]).reshape((2, 1))
p2_velocity = np.array([0, -2]).reshape((2, 1))
p2 = Particle(2, 10, initial_position=p2_position,
              initial_velocity=p2_velocity)

p3_position = np.array([5, 5]).reshape((2, 1))
p3_velocity = np.array([0, 0]).reshape((2, 1))
p3 = Particle(2, 10, initial_position=p3_position,
              initial_velocity=p3_velocity, exhaust_velocity=10)


# Setting Scene #
step_size = 0.1
particle_list = [p1, p2, p3]
update_function = gravitaional_pull_from_list(particle_list)
scene = Scene(particle_list, [
              update_function for p in particle_list], step_size, np.zeros((2,1)))

# Simmulate positions
position_list = []
for _ in range(10 * 5):
    positions = scene.get_positions()
    position_list.append(positions)
    scene.step([(1, np.pi/1000)]*len(particle_list))


paths = list(zip(*position_list))
for path in paths:
    plt.scatter(*zip(*path))

plt.grid(True)
plt.show()

"""Create model"""

class Model:
    def __init__(self, num_states, num_actions, batch_size):
        self._num_states = num_states
        self._num_actions = num_actions
        self._batch_size = batch_size
        # define the placeholders
        self._states = None
        self._actions = None
        # the output operations
        self._logits = None
        self._optimizer = None
        self._var_init = None
        # now setup the model
        self._define_model()

    def _define_model(self):
        self._states = tf.placeholder(shape=[None, self._num_states], dtype=tf.float32)
        self._q_s_a = tf.placeholder(shape=[None, self._num_actions], dtype=tf.float32)
        # create a couple of fully connected hidden layers
        fc1 = tf.layers.dense(self._states, 50, activation=tf.nn.relu)
        fc2 = tf.layers.dense(fc1, 50, activation=tf.nn.relu)
        self._logits = tf.layers.dense(fc2, self._num_actions)
        loss = tf.losses.mean_squared_error(self._q_s_a, self._logits)
        self._optimizer = tf.train.AdamOptimizer().minimize(loss)
        self._var_init = tf.global_variables_initializer()

    def predict_one(self, state, sess):
        return sess.run(self._logits, feed_dict={self._states:
                                                     state.reshape(1, self.num_states)})

    def predict_batch(self, states, sess):
        return sess.run(self._logits, feed_dict={self._states: states})

    def train_batch(self, sess, x_batch, y_batch):
        sess.run(self._optimizer, feed_dict={self._states: x_batch, self._q_s_a: y_batch})

    @property
    def num_states(self):
        return self._num_states

    @property
    def num_actions(self):
        return self._num_actions

    @property
    def batch_size(self):
        return self._batch_size

    @property
    def var_init(self):
        return self._var_init

"""Create Memory Class"""

class Memory:
    def __init__(self, max_memory):
        self._max_memory = max_memory
        self._samples = []

    def add_sample(self, sample):
        self._samples.append(sample)
        if len(self._samples) > self._max_memory:
            self._samples.pop(0)

    def sample(self, no_samples):
        if no_samples > len(self._samples):
            return random.sample(self._samples, len(self._samples))
        else:
            return random.sample(self._samples, no_samples)

Create Runner Class

class GameRunner:
    def __init__(self, sess, model, env, memory, max_eps, min_eps,
                 decay, render=True):
        self._sess = sess
        self._env = env
        self._model = model
        self._memory = memory
        self._render = render
        self._max_eps = max_eps
        self._min_eps = min_eps
        self._decay = decay
        self._eps = self._max_eps
        self._steps = 0
        self._reward_store = []
        self._max_x_store = []

    def run(self):
        state = self._env.reset()
        tot_reward = 0
        max_x = 100
        while True:
            if self._render:
                self._env.render()

            action = self._choose_action(state)
            next_state, reward, done, info = self._env.step(action)

            if self._env.get_distance_to_goal() < max_x:
                max_x = self._env.get_distance_to_goal()
            # is the game complete? If so, set the next state to
            # None for storage sake
            if done:
                next_state = None

            self._memory.add_sample((state, action, reward, next_state))
            self._replay()

            # exponentially decay the eps value
            self._steps += 1
            self._eps = MIN_EPSILON + (MAX_EPSILON - MIN_EPSILON) \
                                      * math.exp(-LAMBDA * self._steps)

            # move the agent to the next state and accumulate the reward
            state = next_state
            tot_reward += reward

            # if the game is done, break the loop
            if done:
                self._reward_store.append(tot_reward)
                self._max_x_store.append(max_x)
                break

        print("Step {}, Total reward: {}, Eps: {}".format(self._steps, tot_reward, self._eps))

    def _choose_action(self, state):
        if random.random() < self._eps:
            return random.randint(0, self._model.num_actions - 1)
        else:
            return np.argmax(self._model.predict_one(state, self._sess))

    def _replay(self):
        batch = self._memory.sample(self._model.batch_size)
        states = np.array([val[0] for val in batch])
        next_states = np.array([(np.zeros(self._model.num_states)
                                 if val[3] is None else val[3]) for val in batch])
        # predict Q(s,a) given the batch of states
        q_s_a = self._model.predict_batch(states, self._sess)
        # predict Q(s',a') - so that we can do gamma * max(Q(s'a')) below
        q_s_a_d = self._model.predict_batch(next_states, self._sess)
        # setup training arrays
        x = np.zeros((len(batch), self._model.num_states))
        y = np.zeros((len(batch), self._model.num_actions))
        for i, b in enumerate(batch):
            state, action, reward, next_state = b[0], b[1], b[2], b[3]
            # get the current q values for all actions in state
            current_q = q_s_a[i]
            # update the q value for action
            if next_state is None:
                # in this case, the game completed after action, so there is no max Q(s',a')
                # prediction possible
                current_q[action] = reward
            else:
                current_q[action] = reward + GAMMA * np.amax(q_s_a_d[i])
            x[i] = state
            y[i] = current_q
        self._model.train_batch(self._sess, x, y)
    
    def get_ship_list(self):
        return self._env.ship.state_list

    @property
    def reward_store(self):
        return self._reward_store

    @property
    def max_x_store(self):
        return self._max_x_store



"""Run with Main"""

if __name__ == "__main__":
    p1_position = np.array([0, 1]).reshape((2, 1))
    p1_velocity = np.array([1, 1]).reshape((2, 1))
    p1 = Particle(3, 10, initial_position=p1_position,
                  initial_velocity=p1_velocity, exhaust_velocity=100)


    p2_position = np.array([0, 0]).reshape((2, 1))
    p2_velocity = np.array([0, 2]).reshape((2, 1))
    p2 = Particle(1, 50, initial_position=p2_position,
                  initial_velocity=p2_velocity)
    step_size = 0.0001
    particle_list = [p1, p2]
    update_funcs = [gravitaional_pull_from_list(particle_list), zero_update_function]
    env = Scene(particle_list=particle_list, update_functions= update_funcs, step_length=step_size, target=np.zeros((2,1)) )

    num_states = 5
    num_actions = 5

    model = Model(num_states, num_actions, BATCH_SIZE)
    mem = Memory(50000)

    with tf.Session() as sess:
        sess.run(model.var_init)
        gr = GameRunner(sess, model, env, mem, MAX_EPSILON, MIN_EPSILON,
                        LAMBDA, render=False)
        num_episodes = 300
        cnt = 0
        while cnt < num_episodes:
            if cnt % 10 == 0:
                print('Episode {} of {}'.format(cnt+1, num_episodes))
                position_list_x = []
                position_list_y = []
                for p in gr.get_ship_list():
                  position_list_x.append(p[1][0])
                  position_list_y.append(p[1][1])
                plt.scatter(position_list_x, position_list_y)
                plt.show()
            gr.run()
            cnt += 1
        plt.plot(gr.reward_store)
        plt.show()
        plt.close("all")
        plt.plot(gr.max_x_store)
        plt.show()

p1.state_list