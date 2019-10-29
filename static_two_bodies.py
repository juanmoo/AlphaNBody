import numpy as np
from particles.classes import Particle, Scene
from particles.physics import gravitaional_pull_from_list, zero_update_function
import matplotlib.pyplot as plt

# Initial Conditions #
p1_position = np.array([-10, 0]).reshape((2, 1))
p1_velocity = np.array([0, 2]).reshape((2, 1))
p1 = Particle(1, 10, initial_position=p1_position,
              initial_velocity=p1_velocity)


p2_position = np.array([10, 0]).reshape((2, 1))
p2_velocity = np.array([0, -2]).reshape((2, 1))
p2 = Particle(2, 10, initial_position=p2_position,
              initial_velocity=p2_velocity)

p3_position = np.array([0, 5]).reshape((2, 1))
p3_velocity = np.array([1, 1]).reshape((2, 1))
p3 = Particle(3, 10, initial_position=p3_position,
              initial_velocity=p3_velocity)


# Setting Scene #
step_size = 0.1
particle_list = [p1, p2, p3]
update_function = gravitaional_pull_from_list(particle_list)
update_function_list = [zero_update_function,
                        zero_update_function, update_function]
scene = Scene(particle_list, update_function_list, step_size)

# Simmulate positions
position_list = []
for _ in range(10 * 5):
    positions = scene.get_positions()
    position_list.append(positions)
    scene.step([0]*len(particle_list))


paths = list(zip(*position_list))
for path in paths:
    plt.scatter(*zip(*path))

plt.grid(True)
plt.show()
