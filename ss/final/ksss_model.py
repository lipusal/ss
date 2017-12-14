#TODO change descript
from ss.final.car import Car

import random
from euclid3 import Vector2
import ss.util.args as arg_base
from ss.util.file_writer import FileWriter

# https://es.wikipedia.org/wiki/Modelo_Knospe,_Santen,_Schadschneider,_Schreckenberg

arg_base.parser.description = "FINAL"
arg_base.parser.add_argument("--num_particles", "-n", help="Number of particles. Default is 10", type=int, default=10)
# Use "width" parameter as road length
arg_base.parser.add_argument("-v_max", "-vm", help="Maximum velocity. Integer. Default is 5 cells/s", type=int, default=20)
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

# TODO parametro
H = 6   # #[s]

# TODO parametrizar y poner valores utiles
P0 = 0.5
PB = 0.94
PD = 0.1

B_S = 7

DELTA_T = 0.1
DELTA_T_SAVE = 0.1


def generate_random_cars():
    """Create particles with random positions on the road"""

    cars = list()

    if args['verbose']:
        print("Generating %i particles without overlap..." % NUM_PARTICLES, end='', flush=True)

    for amount_of_cars in range(NUM_PARTICLES):
        velocity = random.uniform(0, V_MAX)
        # TODO ver que esoty haciendo vx y no vy
        new_car = Car(vx=velocity, acceleration=1, x=random.randint(0, ROAD_LENGTH - 1), y=0, length=CELL_SIZE)

        done = False
        while not done:
            overlap = False
            # Make sure the new particle is at least MIN_DISTANCE from any other existing particle
            velocity = random.uniform(0, V_MAX)
            for existing_particle in cars:
                if existing_particle is not None and new_car.distance_to(existing_particle) < MIN_DISTANCE + velocity:
                    overlap = True
                    # TODO ver que estoy usando vx y no vy
                    new_car = Car(vx=velocity, acceleration=1, x=random.randint(0, ROAD_LENGTH - 1), y=0,
                                       length=CELL_SIZE)
                    break

            done = not overlap

        # TODO hacer que sea un cuadrado no una calle
        cars.append(new_car)

    if args['verbose']:
        print("done")

    return cars


def get_next_car(car, cars):
    next_car = None
    for other_car in cars:
        if car == other_car:
            continue
        if car.x < other_car.x:
            if next_car is None or next_car.x > other_car.x:
                next_car = other_car
    return next_car

t = 0
t_accum = 0
cars = generate_random_cars()
fake_cars = list()
fake_cars.append(Car(0, 0, 0, 0, 0,0))
fake_cars.append(Car(0, ROAD_LENGTH, 0, 0, 0,0))
fake_colors = [(255, 255, 0)] * 2
while t < MAX_TIME:
    new_velocities = list()

    for index, car in enumerate(cars):

        next_car = get_next_car(car, cars)
        if next_car is not None:

            # 0 Rule: Calculation of random parameters
            if abs(car.velocity) == 0:
                p = P0
            if abs(car.velocity) != 0:
                th = car.distance_to(next_car)/ abs(car.velocity)
            ts = min(abs(car.velocity), H)
            if next_car.has_lights_on() and th < ts:
                p = PB
            else:
                p = PD

            # 1st Rule: Acceleration
            if not car.has_lights_on() and not next_car.has_lights_on():
                v = min(abs(car.velocity) + 1, V_MAX)
            elif abs(car.velocity) > 0 and th >= ts:
                v = min(abs(car.velocity) + 1, V_MAX)

            # 2nd Rule: Breaking from interaction with other cars
            next_next_car = get_next_car(next_car, cars)
            # TODO vectorizar bieeeeen!!!
            if next_next_car is not None:
                v_anti = min(next_car.distance_to(next_next_car), abs(next_car.velocity))
            else:
                v_anti = abs(next_car.velocity)
            b_ef = car.distance_to(next_car) + max(v_anti - B_S, 0)
            v = min(v, car.distance_to(next_car))

            # 3rd Rule: Random braking
            if random.uniform(0,1) < p:
                v = max(v - 1, 0)
                # If p = PB
                if next_car.has_lights_on() and abs(car.velocity) > 0 and th < ts:
                    car.turn_on_lights()

            if v < abs(car.velocity):
                car.turn_on_lights()
            else:
                car.turn_off_lights()

            # 4th Rule: Movement
            car.move_by(v*DELTA_T, ROAD_LENGTH)
            car.velocity = Vector2(v, 0)
        else:
            # TODO vectorizar el tema de la velocidad
            car.move_by(DELTA_T*abs(car.velocity), ROAD_LENGTH)

    # Save frame if necessary
    t_accum += DELTA_T
    if t == 0 or t_accum >= DELTA_T_SAVE:
        if args['verbose']:
            print("Saving frame at t=%f" % t)

        # Save particles
        colors = list()     # Real particles are white
        for car in cars:
            if car.bk:
                colors.append((255, 0, 255))
            else:
                colors.append((255, 255, 255))

        # Also save car velocity
        extra_data = lambda car: ("%g" % car.velocity.x)
        FileWriter.export_positions_ovito(cars + fake_cars, t, colors=colors + fake_colors, extra_data_function=extra_data,
                                          mode="w" if t == 0 else "a", output="output.txt")

        # Reset counter
        t_accum = 0

    t += DELTA_T
