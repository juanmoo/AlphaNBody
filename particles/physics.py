import numpy as np
from numpy import linalg as LA

'''
Defines update functions for particles
'''

# Constants
K = 9.81


def gravitaional_pull_from_list(particle_list):
    def update_function(particle, thrust, step_length):
        net_f = np.zeros((2, 1))
        time, position, velocity, fuel = particle.state_list[-1]

        for p in particle_list:
            if p.id != particle.id:
                distance_p = position - p.current_position()
                force_p = - ((K * particle.mass * p.mass)/(LA.norm(distance_p)
                                                           ** 2)) * (distance_p/LA.norm(distance_p))
                net_f += force_p

        # Add Thrust Logic Here #

        #########################

        net_a = net_f/particle.mass
        dv = net_a * step_length
        avg_v = velocity + .5 * dv

        next_time = time + step_length
        next_position = position + avg_v * step_length
        next_velocity = velocity + dv
        next_fuel = fuel

        return (next_time, next_position, next_velocity, next_fuel)
    return update_function
