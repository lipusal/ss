# Add folders to python path to run this from command line
import sys
import os
# NOTE: Adjust the number of ".." to get to the project's root directory (i.e. where doc, ex, and ss are, NOT inside ss
# where cim, util, etc. are)
sys.path.append(os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..")))

import random
import math

from euclid3 import Vector2
import ss.util.args as arg_base
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


def generate_random_cars():
    """Create particles with random positions on the road"""

    result = list()

    if args['verbose']:
        print("Generating %i particles without overlap..." % NUM_PARTICLES, end='', flush=True)

    for particle_count in range(NUM_PARTICLES):
        velocity = random.randint(0, V_MAX)
        new_particle = Particle(x=random.randint(0, ROAD_LENGTH - 1), y=0, radius=CELL_SIZE, v=velocity)

        done = False
        while not done:
            overlap = False
            # Make sure the new particle is at least MIN_DISTANCE from any other existing particle
            velocity = random.randint(0, V_MAX)
            for existing_particle in result:
                if existing_particle is not None and 0 <= new_particle.x - existing_particle.x < MIN_DISTANCE + velocity:
                    overlap = True
                    new_particle = Particle(x=random.randint(0, ROAD_LENGTH - 1), y=0, radius=CELL_SIZE, v=velocity)
                    break

            done = not overlap

        result.append(new_particle)

    if args['verbose']:
        print("done")

    return result


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


def to_circle(x):
    degree = (x / ROAD_LENGTH) * 2 * math.pi
    return math.cos(degree) * ROAD_LENGTH, math.sin(degree) * ROAD_LENGTH


def export_circle(real_particles, t):
    # TODO: Add a more generic and customizable fileWriter method to handle individual rows
    f = open("output.txt", mode="w" if t == 0 else "a")
    f.write("%i\n" % (len(real_particles)*2))
    f.write("%g\n" % t)
    for particle in real_particles:
        x, y = to_circle(particle.x)
        # Export in circle form
        f.write('%i\t%g\t%g' % (particle.id, x, y))
        f.write('\t%g\t%g\t%g' % (255, 255, 255))
        f.write("\t%g\t%g\n" % (particle.radius, particle.velocity.magnitude()))
        # Export in linear form for comparison
        f.write('%i\t%g\t%g' % (particle.id, particle.x, particle.y - ROAD_LENGTH * 2))
        f.write('\t%g\t%g\t%g' % (255, 255, 255))
        f.write("\t%g\t%g\n" % (particle.radius, particle.velocity.magnitude()))
    f.close()

# ----------------------------------------------------------------------------------------------------------------------
#       MAIN
# ----------------------------------------------------------------------------------------------------------------------
if args['time']:
    import ss.util.timer

# Generate random particles or load them from file
cars = generate_random_cars()
# particles = load_particles("in.txt", time=0.)[0:2]

# Generate wall/corner particles
fake_particles = generate_fake_particles()

t_accum = 0
t = 0

while t < MAX_TIME:
    new_velocities = list()

    for car in cars:
        # TODO: Model.evolve()
        if car.velocity.magnitude() <= 1:
            2+2
        # 1) Accelerate
        new_velocity = min(car.velocity.magnitude() + 1, V_MAX)
        if new_velocity <= 1:
            2+2

        # 2) Interaction with cars ahead
        distances = [other.x - car.x for other in cars if other.id != car.id]
        closest_car_distance = min([d for d in distances if d >= 0] or [math.inf])
        new_velocity = min(new_velocity, closest_car_distance - MIN_DISTANCE)
        if new_velocity < 0:
            raise "%s changed velocity!" % car
        if new_velocity <= 1:
            2+2

        # 3) Chance of slowing down
        if random.random() < P:
            new_velocity = max(new_velocity - 1, 0)
        if new_velocity <= 1:
            2+2

        new_velocities.append(new_velocity)

    # Save frame if necessary
    t_accum += DELTA_T
    if t == 0 or t_accum >= DELTA_T_SAVE:
        if args['verbose']:
            print("Saving frame at t=%f" % t)

        # Save particles
        # colors = [(255, 255, 255)] * NUM_PARTICLES     # Real particles are white
        # colors += [(0, 255, 0)] * len(fake_particles)  # Fake particles are green
        export_circle(cars, t)

        # Also save particle radius and velocity for fake particles
        # extra_data = lambda car: ("%g\t%g" % (car.radius, car.velocity.x))
        # FileWriter.export_positions_ovito(fake_particles, t, colors=colors, extra_data_function=extra_data,
        #                                   mode="w" if t == 0 else "a", output="output.txt")

        # Reset counter
        t_accum = 0

    # Evolve road
    evolve_road(cars, new_velocities)

    # Add delta t to total time
    t += DELTA_T

# Simulation complete
print("Done")
