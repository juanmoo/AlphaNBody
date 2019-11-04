import numpy as np

# Classes for simmulator


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

        if initial_position is None:
            initial_position = np.zeros((2, 1))

        if initial_velocity is None:
            initial_velocity = np.zeros((2, 1))
            
        if exhaust_velocity is None:
            exhaust_velocity = 0

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
            (initial_time, initial_position, initial_velocity, initial_fuel, exhaust_velocity)
        ]

    def current_position(self):
        return self.state_list[-1][1]

    def step(self, update_function, thrust, step_length, initial_fuel, exhaust_velocity):
        new_state = update_function(self, thrust, step_length)
        self.state_list.append(new_state)
        return new_state


class Scene(object):
    def __init__(self, particle_list, update_functions, step_length, global_start_time=0):
        self.particle_list = particle_list

        # How each of the particles' position is to be updated
        self.update_functions = update_functions
        self.step_length = step_length

    def get_positions(self):
        return [tuple(p.current_position().flatten()) for p in self.particle_list]

    def step(self, input_thrusts):
        for (particle, update_function, thrust) in \
                zip(self.particle_list, self.update_functions, input_thrusts):

            particle.step(update_function, thrust, self.step_length)
        return self.get_positions()
