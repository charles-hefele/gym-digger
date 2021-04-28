import sys
import numpy as np
import gym
from gym import spaces
from gym.utils import colorize
from io import StringIO

BATTERY_LIFE = 10000

class DiggerEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        # init nutrients
        # self.nutrients_orig = np.array([
        #     [1, 1],
        #     [1, 1]
        # ])

        # init nutrients
        # self.nutrients_orig = np.array([
        #     [0, 0, 1],
        #     [0, 3, 2],
        #     [1, 2, 2]
        # ])

        self.nutrients_orig = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 3, 2, 0, 0, 0, 4, 0, 0],
            [0, 0, 1, 2, 0, 0, 4, 5, 4, 0],
            [0, 0, 0, 0, 0, 0, 0, 4, 0, 0],
            [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 2, 2, 2, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 3, 2, 0],
            [0, 1, 2, 2, 0, 0, 3, 3, 2, 0],
            [0, 0, 3, 3, 0, 0, 0, 2, 2, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ])

        # create a copy to decrement in the simulation
        self.nutrients = np.copy(self.nutrients_orig)

        # set size (assume square)
        self.dim = self.nutrients.shape[0]  # length of one dimension of the matrix
        self.size = self.nutrients.size     # length of the entire matrix

        # game variables
        self.battery = BATTERY_LIFE
        self.score = 0

        # init player loc
        self.row = 0          # top-most cell
        self.col = 0          # left-most cell

        # check for highest value
        highest_nutrient_val = self.nutrients.max()
        highest_robot_pos = self.size - 1
        high = max(highest_nutrient_val, highest_robot_pos)

        # define spaces
        shape = self.size + 1   # the flattened nutrient values grid plus one more slot for the robot position, also flattened
        self.observation_space = spaces.Box(low=0, high=high, shape=(shape,), dtype=np.int)
        self.action_space = spaces.Discrete(5)  # left, down, right, up, dig

        # define vars
        self.done = False
        self.last_action = None

    def step(self, action):
        reward = 0

        # left
        if action == 0:
            if self.col > 0:
                self.battery -= 1
                self.col -= 1

        # down
        if action == 1:
            if self.row < self.nutrients.shape[0] - 1:
                self.battery -= 1
                self.row += 1

        # right
        if action == 2:
            if self.col < self.nutrients.shape[1] - 1:
                self.battery -= 1
                self.col += 1

        # up
        if action == 3:
            if self.row > 0:
                self.battery -= 1
                self.row -= 1

        # dig
        if action == 4:
            self.battery -= 1
            if self.nutrients[self.row][self.col] > 0:
                self.nutrients[self.row][self.col] -= 1
                self.score += 1
                reward = 1
            else:
                reward = -1

        # check done conditions
        if self.battery == 0 or self.nutrients.sum() == 0:
            self.done = True

        # update values
        self.last_action = action

        # bundle the observation up
        bundled_observation = self.bundle_observation()

        # return observation, reward, done, info
        return bundled_observation, reward, self.done, {'battery': self.battery}

    def reset(self):
        self.last_action = None
        self.done = False
        self.battery = BATTERY_LIFE
        self.row = 0          # top-most cell
        self.col = 0          # left-most cell
        self.nutrients = np.copy(self.nutrients_orig)
        return self.bundle_observation()

    def render(self, mode='human'):
        outfile = StringIO() if mode == 'ansi' else sys.stdout
        desc = np.asarray(self.nutrients, dtype='c')
        desc = desc.tolist()
        desc = [[c.decode('utf-8') for c in line] for line in desc]
        desc[self.row][self.col] = colorize(desc[self.row][self.col], "red", highlight=True)

        if self.last_action is not None:
            outfile.write("  ({})\n".format(
                ["Left", "Down", "Right", "Up", "Dig"][self.last_action]))
        else:
            outfile.write("\n")
        outfile.write("\n".join(''.join(line) for line in desc)+"\n")

    def robot_pos(self):
        return self.row * self.dim + self.col

    def bundle_observation(self):
        raveled = self.nutrients.ravel()
        return np.append(raveled, self.robot_pos())
