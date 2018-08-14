# Add folders to python path to run this from command line
import sys
import os
# NOTE: Adjust the number of ".." to get to the project's root directory (i.e. where doc, ex, and ss are, NOT inside ss
# where cim, util, etc. are)
sys.path.append(os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..")))

import random

from euclid3 import Vector2
import ss.util.args as arg_base
from ss.cim.cell_index_method import CellIndexMethod
from ss.util.file_writer import FileWriter
from ss.util.file_reader import FileReader
from ss.cim.particle import Particle

#TODO change descript
arg_base.parser.description = "FINAL"
arg_base.parser.add_argument("--num_particles", "-n", help="Number of particles. Default is 10", type=int, default=10)
# Use "width" parameter as road length
arg_base.parser.add_argument("-v_max", "-vm", help="Maximum velocity. Integer. Default is 5 cells/s", type=int, default=5)
arg_base.parser.add_argument("-b", help="Minimum distance between adjacent cars, in cells. Integer. Default is 1", type=int, default=1)
arg_base.parser.add_argument("-c", help="Chance for cars to reduce their velocity on any given step. Float. "
                                        "Default is 0.3", type=float, default=0.3)
arg_base.parser.add_argument("--size", "-s", help="Cell size. Float. Default is 7.5m", type=float, default=7.5)
arg_base.parser.add_argument("--sim_time", "-tm", help="Simulation time. Float. Default is 100s", type=float, default=100)

args = arg_base.to_dict_no_none()

# Validate params
if not 0 <= args['c'] <= 1:
    raise Exception("p (%g) must be between 0 and 1" % args['p'])
if not args['v_max'] < args['width']:
    raise Exception("Vmax (%g) must be less than width (%g)" % (args['v_max'], args['width']))
if args['num_particles'] < 0:
    raise Exception("Num particles (%i) must be positive" % args['num-particles'])


# Model constants from args, easier to type
NUM_PARTICLES = args['num_particles']
V_MAX = args['v_max']
MIN_DISTANCE = args['b']
P = args['c']
ROAD_LENGTH = int(args['width'])
CELL_SIZE = args['size']
MAX_TIME = args['sim_time']


DELTA_T = 1
DELTA_T_SAVE = 1


def generate_random_board():
    """Create particles with random positions on the road"""

    board = [None] * ROAD_LENGTH

    if args['verbose']:
        print("Generating %i particles without overlap..." % NUM_PARTICLES, end='', flush=True)

    for particle_count in range(NUM_PARTICLES):
        velocity = random.uniform(0, V_MAX)
        new_particle = Particle(x=random.randint(0, ROAD_LENGTH - 1), y=0, radius=CELL_SIZE, v=velocity)

        done = False
        while not done:
            overlap = False
            # Make sure the new particle is at least MIN_DISTANCE from any other existing particle
            velocity = random.uniform(0, V_MAX)
            for existing_particle in board:
                if existing_particle is not None and 0 <= new_particle.distance_to(existing_particle) + existing_particle.radius + new_particle.radius < MIN_DISTANCE + velocity:
                    overlap = True
                    new_particle = Particle(x=random.randint(0, ROAD_LENGTH - 1), y=0, radius=CELL_SIZE, v=velocity)
                    break

            done = not overlap

        board[new_particle.x] = new_particle

    if args['verbose']:
        print("done")

    return board


def generate_fake_particles():
    result = list()

    # Corner particles
    result.append(Particle(0, 0, radius=0, v=0, o=0, is_fake=True))
    result.append(Particle(ROAD_LENGTH, 0, radius=0, v=0, o=0, is_fake=True))

    return result


# def load_particles(in_file, time=None, frame=None):
#     data, properties = FileReader.import_positions_ovito(in_file, time, frame)
#
#     result = list()
#     for i in range(len(data)):
#         id, x, y = data[i]
#         _r, _g, _b, radius, vx, vy = properties[i]
#         v, o = Particle.to_v_o(Vector2(vx, vy))
#         result.append(Particle(x, y, radius=radius, v=v, o=o, id=id))
#
#     return result


def evolve_road(cars, new_velocities):
    for i in range(len(cars)):
        car = cars[i]
        new_velocity = new_velocities[i]

        car.velocity = Particle.to_v_o(Vector2(new_velocity, 0))
        new_position = car.x + new_velocity
        if new_position >= ROAD_LENGTH:
            car.move_to(0, 0)
        else:
            car.move_to(new_position, 0)


# ----------------------------------------------------------------------------------------------------------------------
#       MAIN
# ----------------------------------------------------------------------------------------------------------------------
if args['time']:
    import ss.util.timer

# Generate random particles or load them from file
board = generate_random_board()
cars = [car for car in board if car is not None]
# particles = load_particles("in.txt", time=0.)[0:2]

# Generate wall/corner particles
fake_particles = generate_fake_particles()

t_accum = 0
t = 0

while t < MAX_TIME:
    new_velocities = list()

    for index, car in enumerate(board):
        if car is None:
            continue

        # TODO: Model.evolve()
        # 1) Accelerate
        new_velocity = min(car.velocity.magnitude() + 1, V_MAX)
        # 2) Interaction with cars ahead
        next_cars = [other for other in board[index + 1:] if other is not None]
        if len(next_cars) > 0:
            new_velocity = min(new_velocity, car.distance_to(next_cars[0]) + car.radius + next_cars[0].radius - MIN_DISTANCE)
        # 3) Chance of slowing down
        if random.random() <= P:
            new_velocity = max(new_velocity - 1, 0)

        new_velocities.append(new_velocity)

    # Save frame if necessary
    t_accum += DELTA_T
    if t == 0 or t_accum >= DELTA_T_SAVE:
        if args['verbose']:
            print("Saving frame at t=%f" % t)

        # Save particles
        colors = [(255, 255, 255)] * NUM_PARTICLES     # Real particles are white
        colors += [(0, 255, 0)] * len(fake_particles)  # Fake particles are green
        # Also save particle radius and velocity
        extra_data = lambda car: ("%g\t%g" % (car.radius, car.velocity.x))
        FileWriter.export_positions_ovito(cars + fake_particles, t, colors=colors, extra_data_function=extra_data,
                                          mode="w" if t == 0 else "a", output="output.txt")

        # Reset counter
        t_accum = 0

    # Evolve road
    evolve_road(cars, new_velocities)

    # Add delta t to total time
    t += DELTA_T

# Simulation complete
print("Done")
