# Add folders to python path to run this from command line
import sys
import os
# NOTE: Adjust the number of ".." to get to the project's root directory (i.e. where doc, ex, and ss are, NOT inside ss
# where cim, util, etc. are)
sys.path.append(os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..")))

import math
import random

from euclid3 import Vector2

from ss.cim.cell_index_method import CellIndexMethod
import ss.util.args as arg_base
from ss.util.file_writer import FileWriter
from ss.util.file_reader import FileReader
from ss.cim.particle import Particle
from ss.tp05 import flow_sliding_window

#TODO change descrip
arg_base.parser.description = "Granular media simulation program. Simulates the behavior of sand-like particles " \
                              "falling in a silo with a slit. "
arg_base.parser.add_argument("--num_particles", "-n", help="Number of particles. Default is 100", type=int, default=100)
arg_base.parser.add_argument("-initial_velocity", "-v0", help="Initial velocity. Float. Default is 1 m/s", type=float, default=1)
arg_base.parser.add_argument("-v_max", "-vm", help="Maximum velocity. Float. Default is 3 m/s", type=float, default=3)

args = arg_base.to_dict_no_none()

# Validate params
# if not args['width'] < args['height']:
#     raise Exception("Width (%g) must be less than height (%g)" % (args['width'], args['height']))
# if not args['diameter'] < args['width']:
#     raise Exception("Diameter (%g) must be less than width (%g)" % (args['diameter'], args['width']))
if args['num_particles'] < 0:
    raise Exception("Num particles (%i) must be positive" % args['num-particles'])


# Model constants
MIN_PARTICLE_RADIUS = 0.1           # [m]
MAX_PARTICLE_RADIUS = 0.2           # [m]
V0 = args['initial_velocity']       # [m/s]
MIN_DISTANCE = 0                    # Distance at which particles are considered to collide [m]
# TODO: Confirm these are the proper values
BETA = 1
TAU = 0.5
V_D_MAX = args['v_max']

# Constants from args, easier to type
NUM_PARTICLES = args['num_particles']

# Geometrical constants
HEIGHT = 20
WIDTH = 22
DOOR_POSITION = 20
DIAMETER = 1.2

# Constant positions
DOOR_TOP = Particle(DOOR_POSITION, HEIGHT/2 + DIAMETER/2, radius=0, mass=math.inf, is_fake=True)
DOOR_BOTTOM = Particle(DOOR_POSITION, HEIGHT/2 - DIAMETER/2, radius=0, mass=math.inf, is_fake=True)

# TODO: Should these be params?
DELTA_T = 5e-2
DELTA_T_SAVE = 1e-1


def generate_random_particles():
    """Create particles with random positions in the silo"""

    result = list()

    if args['verbose']:
        print("Generating %i particles without overlap..." % NUM_PARTICLES, end='', flush=True)

    for particle_count in range(NUM_PARTICLES):
        radius = MAX_PARTICLE_RADIUS
        new_particle = Particle.get_random_particle(max_height=HEIGHT - radius - MIN_DISTANCE,
                                                    max_width=DOOR_POSITION - MIN_DISTANCE,
                                                    radius=radius, speed=V0,
                                                    min_height=MIN_DISTANCE,
                                                    min_width=MIN_DISTANCE)
        done = False
        while not done:
            overlap = False
            # Make sure the new particle doesn't overlap with any other existing particle
            radius = MAX_PARTICLE_RADIUS
            for existing_particle in result:
                if new_particle.distance_to(existing_particle) < MIN_DISTANCE + radius:
                    overlap = True
                    new_particle = Particle.get_random_particle(max_height=HEIGHT - radius - MIN_DISTANCE,
                                                                max_width=DOOR_POSITION - MIN_DISTANCE,
                                                                radius=radius, speed=V0,
                                                                min_height=MIN_DISTANCE,
                                                                min_width=MIN_DISTANCE)
                    break

            done = not overlap

        result.append(new_particle)

    if args['verbose']:
        print("done")

    return result


def generate_fake_particles():
    """Generate fake slit particles for visualization, and corner particles for Ovito to create a wall"""

    result = list()

    # Door wall particles
    y = 0
    while y <= HEIGHT:
        if not HEIGHT / 2 - DIAMETER / 2 <= y <= HEIGHT / 2 + DIAMETER / 2:
            result.append(Particle(DOOR_POSITION, y, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
        y += MIN_PARTICLE_RADIUS

    # Corner particles
    result.append(Particle(0, 0, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
    result.append(Particle(WIDTH, 0, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
    result.append(Particle(0, HEIGHT, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
    result.append(Particle(WIDTH, HEIGHT, radius=0, mass=math.inf, v=0, o=0, is_fake=True))

    return result


# FIXME
def load_particles(in_file, time=None, frame=None):
    data, properties = FileReader.import_positions_ovito(in_file, time, frame)

    result = list()
    for i in range(len(data)):
        id, x, y = data[i]
        _r, _g, _b, radius, vx, vy = properties[i]
        v, o = Particle.to_v_o(Vector2(vx, vy))
        result.append(Particle(x, y, radius=radius, v=v, o=o, id=id))

    return result


def add_wall_neighbors(particle, dest):
    """Add fake particles that will represent the wall particles that exert force on the particle"""

    # Check if there is interaction with the bottom wall
    if particle.y <= particle.radius:
        fake = Particle(particle.x, 0, radius=0, mass=math.inf, is_fake=True)
        dest.append((fake, particle.distance_to(fake)))

    # Check if there is interaction with top wall
    if particle.y + particle.radius >= HEIGHT:
        fake = Particle(particle.x, 0, radius=0, mass=math.inf, is_fake=True)
        dest.append((fake, particle.distance_to(fake)))

    # Check if there is interaction with the left wall
    if particle.x <= particle.radius:
        fake = Particle(0, particle.y, radius=0, mass=math.inf, is_fake=True)
        dest.append((fake, particle.distance_to(fake)))

    # Check if there is interaction with the right wall
    if particle.x <= DOOR_POSITION and not DOOR_BOTTOM.y <= particle.y <= DOOR_TOP.y:
        fake = Particle(DOOR_POSITION, particle.y, radius=0, mass=math.inf, is_fake=True)
        if particle.distance_to(fake) <= particle.radius:
            dest.append((fake, particle.distance_to(fake)))


def evolve_particles(particles, new_positions, new_velocities, new_radii):
    result = []
    for i in range(len(particles)):
        p = particles[i]
        #TODO que hacemos con las particulas que se van?
        if new_positions[i].x < WIDTH:
            p.position = new_positions[i]
            p.velocity = Particle.to_v_o(new_velocities[i])
            p.radius = new_radii[i]
            result.append(p)
        # Discard particles that have exited the room

    return result


def target(particle):
    if particle.y > DOOR_TOP.y:
        # Above door => target top edge of door
        return Particle(DOOR_POSITION, DOOR_TOP.y - particle.radius, radius=0, mass=math.inf, is_fake=True)
    elif particle.y < DOOR_BOTTOM.y:
        # Below door => target bottom edge of door
        return Particle(DOOR_POSITION, DOOR_BOTTOM.y + particle.radius, radius=0, mass=math.inf, is_fake=True)
        return DOOR_BOTTOM
    else:
        # Within door => target edge of room straight ahead
        return Particle(WIDTH, particle.y, is_fake=True)


def evolve_no_contact(particle):
    # Magnitude
    new_velocity = V_D_MAX * ((particle.radius - MIN_PARTICLE_RADIUS) / (MAX_PARTICLE_RADIUS - MIN_PARTICLE_RADIUS))**BETA
    # Vector
    # TODO: Make target a function
    new_velocity = new_velocity * particle.relative_position(target(particle)).normalize()

    new_position = particle.position + new_velocity * DELTA_T

    new_radius = particle.radius
    if particle.radius < MAX_PARTICLE_RADIUS:
        new_radius += MAX_PARTICLE_RADIUS / TAU * DELTA_T

    return new_position, new_velocity, new_radius


def evolve_contact(particle, others):
    escape_velocity = Vector2()
    for other, _ in others:
        escape_velocity += particle.relative_position(other).normalize() * -1 * V_D_MAX

    new_position = particle.position + escape_velocity * DELTA_T

    return new_position, escape_velocity, MIN_PARTICLE_RADIUS


# ----------------------------------------------------------------------------------------------------------------------
#       MAIN
# ----------------------------------------------------------------------------------------------------------------------
if args['time']:
    import ss.util.timer

# Generate random particles or load them from file
particles = generate_random_particles()
# particles = load_particles("in.txt", time=0.)[0:2]

# Generate wall/corner particles
fake_particles = generate_fake_particles()

t_accum = 0
t = 0
pedestrians_who_exited = 0

while len(particles) > 0:
    # Calculate all neighbors for all particles
    neighbors = CellIndexMethod(particles, radius=MAX_PARTICLE_RADIUS, width=WIDTH, height=HEIGHT).neighbors
    # Initialize variables
    new_positions, new_velocities, new_radii = [], [], []
    total_velocities = 0

    for p in particles:

        # Add fake particles to represent walls
        # TODO CHECK
        add_wall_neighbors(p, neighbors[p.id])
        colliding = next((True for _, distance in neighbors[p.id] if distance < MIN_DISTANCE), False)

        new_position, new_velocity, new_radius = evolve_contact(p, neighbors[p.id]) if colliding else evolve_no_contact(p)

        if p.position.x <= DOOR_POSITION < new_position.x:
            # FIXME: Some pedestrians go back through the door for some reason, so we register them again when they re-exit
            pedestrians_who_exited += 1
            flow_sliding_window.append_event("flow_n.txt", pedestrians_who_exited, t, "w" if pedestrians_who_exited == 1 else "a")

        # Save new position and velocity
        new_positions.append(new_position)
        new_velocities.append(new_velocity)
        new_radii.append(new_radius)

    # Save frame if necessary
    t_accum += DELTA_T
    if t == 0 or t_accum >= DELTA_T_SAVE:
        if args['verbose']:
            print("Saving frame at t=%f" % t)

        # Save particles
        colors = [(255, 255, 255)] * len(particles)  # Real particles are white
        colors += [(0, 255, 0)] * len(fake_particles)  # Fake particles are green
        # Also save particle radius and velocity
        extra_data = lambda particle: ("%g\t%g\t%g" % (MIN_PARTICLE_RADIUS, particle.velocity.x, particle.velocity.y))
        FileWriter.export_positions_ovito(particles + fake_particles, t, colors=colors, extra_data_function=extra_data,
                                          mode="w" if t == 0 else "a", output="output.txt")

        # Save Flow
        file = open("flow.txt", "w" if t == 0 else "a")
        file.write("%g,%g\n" % (t, pedestrians_who_exited / DELTA_T_SAVE))
        file.close()

        # Reset counter
        t_accum = 0

    # Evolve particles
    particles = evolve_particles(particles, new_positions, new_velocities, new_radii)

    # Add delta t to total time
    t += DELTA_T
