import math
import random

from euclid3 import Vector2

from ss.cim.cell_index_method import CellIndexMethod
import ss.util.args as arg_base
from ss.util.file_writer import FileWriter
from ss.util.file_reader import FileReader
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
arg_base.parser.add_argument("--num_particles", "-n", help="Number of particles. Default is 100", type=int, default=100)

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
MAX_PARTICLE_RADIUS = 0.015 # [m]
SLIT_Y = args['height']/10  # Y coordinate at which the slit is located [m].
MIN_Y = 0                   # Min Y coordinate of particles [m]. When below this, they are repositioned at the top with V=0
V0 = 0                      # [m/s]

# Constant vectors
X = Vector2(1, 0)           # Unit vector X
Y = Vector2(0, 1)           # Unit vector Y
G = -Y * 9.81               # Gravity vector

# Constants from args, easier to type
NUM_PARTICLES = args['num_particles']
HEIGHT = args['height'] + SLIT_Y
WIDTH = args['width']
DIAMETER = args['diameter']

MIN_DISTANCE = 0            # Min distance between created particles [m]. Note that for this simulation, once the
                            # simulation has started particles may be closer than this. This is just for the start.

# TODO: Should these be params?
DELTA_T = 1e-5
DELTA_T_SAVE = 1e-2


def generate_random_particles():
    """Create particles with random positions in the silo"""

    result = list()

    if args['verbose']:
        print("Generating %i particles without overlap..." % NUM_PARTICLES, end='', flush=True)

    for particle_count in range(NUM_PARTICLES):
        radius = random.uniform(MIN_PARTICLE_RADIUS, MAX_PARTICLE_RADIUS)
        new_particle = Particle.get_random_particle(max_height=HEIGHT - radius - MIN_DISTANCE,
                                                    max_width=WIDTH - radius - MIN_DISTANCE,
                                                    radius=radius, speed=V0, mass=PARTICLE_MASS,
                                                    min_height=SLIT_Y + MIN_DISTANCE, min_width=MIN_DISTANCE)
        done = False
        while not done:
            overlap = False
            # Make sure the new particle doesn't overlap with any other existing particle
            radius = random.uniform(MIN_PARTICLE_RADIUS, MAX_PARTICLE_RADIUS)
            for existing_particle in result:
                if new_particle.distance_to(existing_particle) < MIN_DISTANCE + radius:
                    overlap = True
                    new_particle = Particle.get_random_particle(max_height=HEIGHT - radius - MIN_DISTANCE,
                                                                max_width=WIDTH - radius - MIN_DISTANCE,
                                                                radius=radius, speed=V0, mass=PARTICLE_MASS,
                                                                min_height=SLIT_Y + MIN_DISTANCE,
                                                                min_width=MIN_DISTANCE)
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
        if not WIDTH / 2 - DIAMETER / 2 <= x <= WIDTH / 2 + DIAMETER / 2:
            result.append(Particle(x, SLIT_Y, radius=MIN_PARTICLE_RADIUS, mass=math.inf, v=0, o=0, is_fake=True))
        x += MIN_PARTICLE_RADIUS

    # Corner particles
    result.append(Particle(0, 0, radius=MIN_PARTICLE_RADIUS, mass=math.inf, v=0, o=0, is_fake=True))
    result.append(Particle(WIDTH, 0, radius=MIN_PARTICLE_RADIUS, mass=math.inf, v=0, o=0, is_fake=True))
    result.append(Particle(0, HEIGHT, radius=MIN_PARTICLE_RADIUS, mass=math.inf, v=0, o=0, is_fake=True))
    result.append(Particle(WIDTH, HEIGHT, radius=MIN_PARTICLE_RADIUS, mass=math.inf, v=0, o=0, is_fake=True))

    return result


def load_particles(in_file, time=None, frame=None):
    data, properties = FileReader.import_positions_ovito(in_file, time, frame)

    result = list()
    for i in range(len(data)):
        id, x, y = data[i]
        _r, _g, _b, radius, vx, vy = properties[i]
        v, o = Particle.to_v_o(Vector2(vx, vy))
        result.append(Particle(x, y, radius=radius, mass=PARTICLE_MASS, v=v, o=o, id=id))

    return result


def add_wall_neighbors(particle, dest):
    """Add fake particles that will represent the wall particles that exert force on the particle"""

    # Check if there is interaction with the bottom wall
    if particle.y >= SLIT_Y and (particle.x <= (WIDTH - DIAMETER) / 2 or particle.x > (WIDTH + DIAMETER) / 2):
        fake = Particle(particle.x, SLIT_Y, radius=0, mass=math.inf, is_fake=True)
        if superposition(particle, fake) >= 0:
            dest.append((Particle(particle.x, SLIT_Y, radius=0, mass=math.inf, is_fake=True), particle.distance_to(fake)))

    # Check if there is interaction with the left wall
    if particle.x <= particle.radius:
        fake = Particle(0, particle.y, radius=0, mass=math.inf, is_fake=True)
        dest.append((fake, particle.distance_to(fake)))

    # Check if there is interaction with the right wall
    if WIDTH - particle.x <= particle.radius:
        fake = Particle(WIDTH, particle.y, radius=0, mass=math.inf, is_fake=True)
        dest.append((fake, particle.distance_to(fake)))


def superposition(particle, other):
    if other.is_fake:
        # Wall particle
        return particle.radius - (other.position - particle.position).magnitude()
    else:
        # Real particle
        return particle.radius + other.radius - (other.position - particle.position).magnitude()


def calculate_force(particle, others):
    f_x = f_y = 0
    for n, _ in others:
        epsilon = superposition(particle, n)
        if epsilon >= 0:
            v_n = particle.relative_position(n).normalize()
            fn, ft = f_n(particle, n), f_t(particle, n)

            f_x += fn * v_n.x + ft * (-v_n.y)
            f_y += fn * v_n.y + ft * v_n.x

    return Vector2(f_x, f_y)


def f_t(particle, neighbor):
    v_n = particle.relative_position(neighbor).normalize()
    v_t = Vector2(-v_n.y, v_n.x)
    return K_t * superposition(particle, neighbor) * particle.relative_velocity(neighbor).dot(v_t)


def f_n(particle, neighbor):
    return -K_n * superposition(particle, neighbor)


def evolve_particles(particles, new_positions, new_velocities, pending_particles):
    """Update all particles' positions and velocities. For those that have fallen below MIN_Y, delete them and create
    new ones (with the same ID) on the top of the silo, with V = 0, ensuring no overlap. Also, for the new particles
    set previous position and velocity to the same as the starting ones. If we simulate with Euler, the simulation
    would give us a previous position and velocity as if the particle had been thrown up and it was now starting to
    fall down, but this is incorrect. Better to make it like the particle was being held where it is now, and is now
    being dropped.

    :return A tuple of lists of the form (evolved_particles, pending_particles), where `pending_particles` are particles
    that could not be repositioned (ie. there was no room on the top of the silo). We should attempt to add these
    particles again in the next delta_t."""

    evolved_particles, fallen_particles, new_pending_particles = [], [], []

    for i in range(len(particles)):
        p = particles[i]
        new_position = new_positions[i]

        if new_position.y <= MIN_Y or new_position.y > HEIGHT:
            # Particle either fell below, or to the side but is below the slit, reset
            fallen_particles.append(p)
        else:
            # Evolve normally
            p.position = new_position
            p.velocity = Particle.to_v_o(new_velocities[i])
            evolved_particles.append(p)

    # Now that all regular particles have evolved, reposition pending and fallen particles ensuring no overlap (pending first)
    for p in pending_particles + fallen_particles:
        # Replace with new particle
        # TODO: Ensure no overlap. If can't generate without overlap, choose random X
        overlap = True
        new_x = p.x
        # Avoid respawning too close to side walls
        if new_x < MIN_DISTANCE:
            new_x = MIN_DISTANCE
        elif WIDTH - new_x < MIN_DISTANCE:
            new_x = WIDTH - MIN_DISTANCE

        overlap_attempts = 0
        while overlap and overlap_attempts < 100:
            new_particle = Particle(new_x, HEIGHT - p.radius - MIN_DISTANCE, radius=p.radius, mass=p.mass, v=0, o=0,
                                    id=p.id)
            if len(evolved_particles) == 0:
                overlap = False
            for p2 in evolved_particles:
                overlap = new_particle.distance_to(p2) < MIN_DISTANCE
                if overlap:
                    print("Overlap between #%i and #%i, setting random X for #%i" % (p.id, p2.id, p.id))
                    new_x = random.uniform(MIN_DISTANCE, WIDTH - MIN_DISTANCE)
                    break

            overlap_attempts += 1

        if overlap:
            # Couldn't find room for this particle, try again later
            print("Couldn't reposition particle #%i, will try again later" % p.id)
            new_pending_particles.append(p)
        else:
            # Update position and velocity with same values so previous_position and previous_velocity are the same as current
            new_particle.position = new_particle.position
            # TODO: Make setter receive Vector2 by default
            new_particle.velocity = (new_particle.vel_module(), new_particle.vel_angle())

            evolved_particles.append(new_particle)

    for p in evolved_particles:
        if p.x < 0 or p.x > WIDTH or p.y > HEIGHT:
            raise Exception("%s is out of bounds, max coordinates are (%g,%g)" % (p, WIDTH, HEIGHT))

    return evolved_particles, new_pending_particles


# ----------------------------------------------------------------------------------------------------------------------
#       MAIN
# ----------------------------------------------------------------------------------------------------------------------
if args['time']:
    import ss.util.timer

# Generate random particles or load them from file
particles = generate_random_particles()
# particles = load_particles("in.txt", time=0.)[0:2]
pending_particles = list()      # See evolve_particles

# Generate wall/corner particles
fake_particles = generate_fake_particles()

t_accum = 0
t = 0
num_fallen_particles = 0
# TODO: Establish end condition
while True:

    # Calculate all neighbors for all particles
    neighbors = CellIndexMethod(particles, radius=MAX_PARTICLE_RADIUS, width=WIDTH, height=HEIGHT).neighbors

    # Initialize variables
    new_positions, new_velocities = [], []
    for p in particles:

        # Add fake particles to represent walls
        # TODO CHECK
        add_wall_neighbors(p, neighbors[p.id])

        # Calculate total force exerted on p on the normal and tang
        # TODO check
        force = calculate_force(p, neighbors[p.id]) + (p.mass * G)

        # Calculate new position and new velocity for particle
        # TODO ver lo de usar gear predictor
        new_position = verlet.r(particle=p, delta_t=DELTA_T, force=force)
        new_velocity = verlet.v(p, DELTA_T, force)

        if p.position.y >= SLIT_Y and new_position.y < SLIT_Y:
            num_fallen_particles += 1

        # Save new position and velocity
        new_positions.append(new_position)
        new_velocities.append(new_velocity)

    # Save frame if necessary
    t_accum += DELTA_T
    if t == 0 or t_accum >= DELTA_T_SAVE:
        if args['verbose']:
            print("Saving frame at t=%f" % t)

        # Save particles
        colors = [(255, 255, 255)] * len(particles)  # Real particles are white
        colors += [(0, 255, 0)] * len(fake_particles)  # Fake particles are green
        # Also save particle radius and velocity
        extra_data = lambda particle: ("%g\t%g\t%g" % (particle.radius, particle.velocity.x, particle.velocity.y))
        FileWriter.export_positions_ovito(particles + fake_particles, t, colors=colors, extra_data_function=extra_data,
                                          mode="w" if t == 0 else "a", output="output.txt")

        # Save Flow
        file = open("flow.txt", "w" if t == 0 else "a")
        file.write("%g,%g\n" % (t, num_fallen_particles/DELTA_T_SAVE))
        file.close()
        num_fallen_particles = 0

        # Reset counter
        t_accum = 0

    # Evolve particles
    particles, pending_particles = evolve_particles(particles, new_positions, new_velocities, pending_particles)

    # Add delta t to total time
    t += DELTA_T
