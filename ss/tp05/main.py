import math
import random

from euclid3 import Vector2

from ss.cim.cell_index_method import CellIndexMethod
import ss.util.args as arg_base
from ss.util.file_writer import FileWriter
from ss.cim.particle import Particle
from ss.tp04.solutions import verlet

# TODO: Update description
arg_base.parser.description = "Gas Diffusion simulation Program. Simulates how a number of given gas particles " \
                              "diffuse from one compartment to another through a slit. Unlike TP03, particles in this" \
                              "simulation have interaction forces as modeled by the Lennard-Jones potential model"
# arg_base.parser.add_argument("--height", "-h", help="Silo height [meters], float.  Default is 50", type=float, default=50)
# arg_base.parser.add_argument("--width", "-w", help="Silo width [meters], float.  Must be less than height. Default is "
#                                                    "20", type=float, default=20)
arg_base.parser.add_argument("--diameter", "-d", help="Diameter of bottom silo opening [meters], float.  Must be less "
                                                      "than width. Default is 0.5", type=float, default=0.5)
arg_base.parser.add_argument("--num_particles", "-n", help="Number of particles. Default is 500", type=int, default=50)

args = arg_base.to_dict_no_none()

# Validate params
if not args['width'] < args['height']:
    raise Exception("Width (%g) must be less than height (%g)" % (args['width'], args['height']))
if not args['diameter'] < args['width']:
    raise Exception("Diameter (%g) must be less than width (%g)" % (args['diameter'], args['width']))
if args['num_particles'] < 0:
    raise Exception("Num particles (%i) must be positive" % args['num-particles'])


# Constants
K_n = 10e5                  # Kn, ?? [N/m]
K_t = 2*K_n                 # Kt, ?? [N/m]
PARTICLE_MASS = 0.01        # [Kg]
MIN_PARTICLE_RADIUS = 0.01  # [m]
MAX_PARTICLE_RADIUS = 0.03  # [m]
MIN_Y = -args['height']/10  # Min Y coordinate of particles [m]. When below this, they are repositioned at the top with V=0
V0 = 0                      # [m/s]

# Constant vectors
X = Vector2(1, 0)           # Unit vector X
Y = Vector2(0, 1)           # Unit vector Y
G = -Y * 9.81               # Gravity vector

# Constants from args, easier to type
NUM_PARTICLES = args['num_particles']
HEIGHT = args['height']
WIDTH = args['width']
DIAMETER = args['diameter']

MIN_DISTANCE = 0            # Min distance between created particles [m]. Note that for this simulation, once the
                            # simulation has started particles may be closer than this. This is just for the start.

# TODO: Should these be params?
delta_t = 0.00006
DELTA_T_SAVE = 0.05


def generate_random_particles():
    """Create particles with random positions in the silo"""

    result = list()

    if args['verbose']:
        print("Generating %i particles without overlap..." % NUM_PARTICLES, end='', flush=True)

    for particle_count in range(NUM_PARTICLES):
        radius = random.uniform(MIN_PARTICLE_RADIUS, MAX_PARTICLE_RADIUS)
        new_particle = Particle.get_random_particle(max_height=HEIGHT - MIN_DISTANCE, max_width=WIDTH / 2 - radius - MIN_DISTANCE,
                                                    radius=radius, speed=V0, mass=PARTICLE_MASS, min_height=MIN_DISTANCE, min_width=MIN_DISTANCE)
        done = False
        while not done:
            overlap = False
            # Make sure the new particle doesn't overlap with any other existing particle
            radius = random.uniform(MIN_PARTICLE_RADIUS, MAX_PARTICLE_RADIUS)
            for existing_particle in result:
                if new_particle.distance_to(existing_particle) < MIN_DISTANCE + radius:
                    overlap = True
                    new_particle = Particle.get_random_particle(max_height=HEIGHT - MIN_DISTANCE,
                                                                max_width=WIDTH / 2 - radius - MIN_DISTANCE,
                                                                radius=radius, speed=V0, mass=PARTICLE_MASS,
                                                                min_height=MIN_DISTANCE, min_width=MIN_DISTANCE)
                    break

            done = not overlap

        result.append(new_particle)

    if args['verbose']:
        print("done")

    return result


def generate_fake_particles():
    """Generate fake slit particles for visualization, and corner particles for Ovito to create a wall"""

    x = 0
    result = list()
    # Slit particles
    while x <= WIDTH:
        if not WIDTH/2 - DIAMETER/2 <= x <= WIDTH/2 + DIAMETER/2:
            result.append(Particle(x, 0, radius=MIN_PARTICLE_RADIUS, mass=math.inf, v=0, o=0, is_fake=True))
        x += MIN_PARTICLE_RADIUS

    # Corner particles
    result.append(Particle(0, 0, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
    result.append(Particle(WIDTH, 0, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
    result.append(Particle(0, HEIGHT, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
    result.append(Particle(WIDTH, HEIGHT, radius=0, mass=math.inf, v=0, o=0, is_fake=True))

    return result

#
# def load_particles(positions, properties=None):
#     if properties is not None and len(positions) != len(properties):
#         raise Exception("Positions and properties must have the same length")
#
#     result = list()
#     for i in range(len(positions)):
#         position = positions[i]
#         # TODO: Store velocity angle in output
#         result.append(Particle(position[0], position[1], radius=PARTICLE_RADIUS, mass=PARTICLE_MASS, v=V0, o=random.uniform(0, 2 * math.pi)))
#
#     return result


# def add_wall_neighbors(particle, dest):
#     """Add fake particles that will represent the wall particles that exert force on the particle"""
#
#     # Check if there is interaction with the left wall
#     if particle.x <= R:
#         dest.append((Particle(x=0, y=particle.y, mass=math.inf, is_fake=True), particle.x))
#
#     # Check if there is interaction with the bottom wall
#     if particle.y <= R:
#         dest.append((Particle(x=particle.x, y=0, mass=math.inf, is_fake=True), particle.y))
#
#     # Check if there is interaction with the right wall
#     if WIDTH - particle.x <= R:
#         dest.append((Particle(x=WIDTH, y=particle.y, mass=math.inf, is_fake=True), particle.x))
#
#     # Check if there is interaction with the top wall
#     if HEIGHT - particle.y <= R:
#         dest.append((Particle(x=particle.x, y=HEIGHT, mass=math.inf, is_fake=True), particle.y))
#
#     # Is particle within the slit in Y?
#     if HEIGHT/2 - SLIT_SIZE/2 < particle.y < HEIGHT/2 + SLIT_SIZE/2:
#         # Yes - check interaction with slit corners if appropriate
#         for p2 in [SLIT_TOP, SLIT_BOTTOM]:
#             d = particle.distance_to(p2)
#             if d <= R:
#                 dest.append((p2, d))
#     else:
#         # No - check interaction with middle wall horizontally
#         if abs(particle.x - WIDTH/2) <= R:
#             dest.append((Particle(x=WIDTH / 2, y=particle.y, mass=math.inf, is_fake=True), abs(particle.x - WIDTH / 2)))


# def calculate_force(particle, neighbors):
#     """Calculate total force exerted on particle by neighbors with the lennard jones force"""
#     force_x = 0
#     force_y = 0
#     for neighbor, _ in neighbors:
#         if neighbor != particle:
#             # Check if the neighbor particle is not in the same compartment as the original particle
#             if not neighbor.is_fake and compartment(particle) != compartment(neighbor):
#                 # TODO hacer lo de Barto de la pendiente para ver si se ven las partículas entre la ranura
#                 continue
#
#             # Calculate total force magnitude
#             dist = particle.distance_to(neighbor)
#             force = lennard_jones_force(dist)
#             # Calculate angle between neighbor and particle
#             angle = math.atan2(particle.y-neighbor.y, particle.x-neighbor.x)
#             # Project the force on each axis component
#             force_x += force * math.cos(angle)
#             force_y += force * math.sin(angle)
#     return force_x, force_y

def superposition(particle, other):
    if other.is_fake:
        # Wall particle
        return particle.radius - (other.position - particle.position).magnitude()
    else:
        # Real particle
        return particle.radius + other.radius - (other.position - particle.position).magnitude()



def calculate_force(particle, others):
    # TODO check
    fn = 0
    ft = 0
    for n in others:
        v_t = particle.relative_position(n).normalize()
        v_n = Vector2(-v_t.y, v_t.x)
        epsilon = superposition(particle, n)
        if epsilon >= 0:
            fn += -K_n * epsilon * v_n
            ft += K_t * epsilon * particle.relative_position(n) * v_t
    return fn, ft


# ----------------------------------------------------------------------------------------------------------------------
#       MAIN
# ----------------------------------------------------------------------------------------------------------------------
if args['time']:
    import ss.util.timer

# Generate random particles
particles = generate_random_particles()

# Load particles from file
# from ss.util.file_reader import FileReader
# positions, properties = FileReader.import_positions_ovito("/Users/juanlipuma/PycharmProjects/ss/in.txt", time=48.444)
# particles = load_particles(positions, properties)[0:100]
# NUM_PARTICLES = 100

# Generate wall/corner particles
fake_particles = generate_fake_particles()

t_accum = 0
t = 0

# TODO: Establish end condition
while True:

    # Calculate all neighbors for all particles
    neighbors = CellIndexMethod(particles, radius=MAX_PARTICLE_RADIUS, width=WIDTH, height=HEIGHT).neighbors

    # Initialize variables
    new_positions, new_velocities = [], []
    for p in particles:

        # Add fake particles to represent walls
        #  TODO
        # add_wall_neighbors(p, neighbors[p.id])

        # Calculate total force exerted on p on the normal and tang
        # TODO check
        f_norm, f_tang = calculate_force(p, neighbors[p.id])
        force = f_norm + f_tang + (p.mass * G)

        # Calculate new position and velocity using Verlet
        # TODO ver lo de usar gear predictor
        new_position = verlet.r(particle=p, delta_t=delta_t, force=force)

        # Calculate new position and new velocity for particle
        new_positions.append(new_position)
        new_velocity = verlet.v(p, delta_t, force)
        new_velocities.append(new_velocity)

        if new_position.x < 0 or new_position.y < 0 or new_position.x > WIDTH or new_position.y > HEIGHT:
            raise Exception("The particle moved out of the bounds, x:%f y:%f, width: %f, height: %f" %(new_position.x, new_position.y, WIDTH, HEIGHT))

    # Save frame if necessary
    t_accum += delta_t
    if t == 0 or t_accum >= DELTA_T_SAVE:
        if args['verbose']:
            print("Saving frame at t=%f" % t)

        # Save particles
        colors = [(255, 255, 255)] * NUM_PARTICLES      # Real particles are white
        colors += [(0, 255, 0)] * len(fake_particles)   # Fake particles are green
        # Also save particle radius and velocity
        extra_data = lambda particle: ("%g\t%g\t%g", particle.radius, particle.velocity.x, particle.velocity.y)
        FileWriter.export_positions_ovito(particles + fake_particles, t, colors=colors, extra_data_function=extra_data, mode="w" if t == 0 else "a", output="output2.txt")

        # Save kinetic and potential energy for current time
        # # Used for 2.2
        # file = open("energy2.txt", "w" if t == 0 else "a")
        # file.write("%g,%g,%g\n" % (t, e_k, e_u))
        # file.close()

        # Reset counter
        t_accum = 0

    # Evolve particles
    for i in range(len(particles)):
        particles[i].position = new_positions[i]
        particles[i].velocity = new_velocities[i]

    # Add delta t to total time
    t += delta_t
