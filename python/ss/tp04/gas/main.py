import math
import random

import numpy as np
from euclid3 import Vector2
import matplotlib.pyplot as plt

from ss.cim.cell_index_method import CellIndexMethod
import ss.util.args as arg_base
from ss.util.file_writer import FileWriter
from ss.cim.particle import Particle
from ss.tp04.solutions import verlet

arg_base.parser.description = "Gas Diffusion simulation Program. Simulates how a number of given gas particles " \
                              "diffuse from one compartment to another through a slit. Unlike TP03, particles in this" \
                              "simulation have interaction forces as modeled by the Lennard-Jones potential model"
args = arg_base.to_dict_no_none()

# Constants
R_M = 1         # Rm, distance of minimum potential.If particles are closer than this, they are repelled [dimensionless]
EPSILON = 2     # ε, depth of potential well [J]
M = 0.1         # Particle mass [dimensionless]
V0 = 10         # Initial particle speed [dimensionless]
R = 5           # Maximum interaction distance [dimensionless]
WIDTH = 100     # Area width. Each compartment has width WIDTH/2 [dimensionless]
HEIGHT = 50     # Area height [dimensionless]
SLIT_SIZE = 5   # [dimensionless]
NUM_PARTICLES = 100
PARTICLE_RADIUS = 0
# Guard to make sure all particles are at least this distance from each other in
# the beginning, to avoid really strong forces before the first iteration
MIN_DISTANCE = 2

delta_t = 0.00006
DELTA_T_SAVE = 0.05


def generate_random_particles():
    """Create particles with random positions in the box"""

    result = list()

    if args['verbose']:
        print("Generating %i particles without overlap..." % NUM_PARTICLES, end='', flush=True)

    for particle_count in range(NUM_PARTICLES):
        new_particle = Particle.get_random_particle(max_height=HEIGHT - MIN_DISTANCE, max_width=WIDTH / 2 - PARTICLE_RADIUS - MIN_DISTANCE,
                                                    radius=PARTICLE_RADIUS, speed=V0, mass=M, min_height=MIN_DISTANCE, min_width=MIN_DISTANCE)
        done = False
        while not done:
            overlap = False
            # Make sure the new particle doesn't overlap with any other existing particle
            for existing_particle in result:
                if new_particle.distance_to(existing_particle) < MIN_DISTANCE + PARTICLE_RADIUS:
                    overlap = True
                    new_particle = Particle.get_random_particle(max_height=HEIGHT - MIN_DISTANCE,
                                                                max_width=WIDTH / 2 - PARTICLE_RADIUS - MIN_DISTANCE,
                                                                radius=PARTICLE_RADIUS, speed=V0, mass=M,
                                                                 min_height=MIN_DISTANCE, min_width=MIN_DISTANCE)
                    break

            done = not overlap

        result.append(new_particle)

    if args['verbose']:
        print("done")

    return result


def generate_fake_particles():
    """Generate fake middle wall particles for visualization, and corner particles for Ovito to create a wall"""

    y = 0.0
    result = list()
    # Wall particles
    while y <= HEIGHT:
        if not HEIGHT / 2 - SLIT_SIZE / 2 + PARTICLE_RADIUS < y < HEIGHT / 2 + SLIT_SIZE / 2 - PARTICLE_RADIUS:
            result.append(Particle(WIDTH / 2, y, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
        y += 1

    # Corner particles
    result.append(Particle(0, 0, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
    result.append(Particle(WIDTH, 0, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
    result.append(Particle(0, HEIGHT, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
    result.append(Particle(WIDTH, HEIGHT, radius=0, mass=math.inf, v=0, o=0, is_fake=True))

    return result


def load_particles(positions, properties=None):
    if properties is not None and len(positions) != len(properties):
        raise Exception("Positions and properties must have the same length")

    result = list()
    for i in range(len(positions)):
        position = positions[i]
        # TODO: Store velocity angle in output
        result.append(Particle(position[0], position[1], radius=PARTICLE_RADIUS, mass=M, v=V0, o=random.uniform(0, 2*math.pi)))

    return result


def add_wall_neighbors(particle, dest):
    """Add fake particles that will represent the wall particles that exert force on the particle"""

    # Check if there is interaction with the left wall
    if particle.x <= R:
        dest.append((Particle(x=0, y=particle.y, mass=math.inf, is_fake=True), particle.x))

    # Check if there is interaction with the bottom wall
    if particle.y <= R:
        dest.append((Particle(x=particle.x, y=0, mass=math.inf, is_fake=True), particle.y))

    # Check if there is interaction with the right wall
    if WIDTH - particle.x <= R:
        dest.append((Particle(x=WIDTH, y=particle.y, mass=math.inf, is_fake=True), WIDTH - particle.x))

    # Check if there is interaction with the top wall
    if HEIGHT - particle.y <= R:
        dest.append((Particle(x=particle.x, y=HEIGHT, mass=math.inf, is_fake=True), HEIGHT - particle.y))

    # Is particle within the slit in Y?
    if HEIGHT/2 - SLIT_SIZE/2 < particle.y < HEIGHT/2 + SLIT_SIZE/2:
        # Yes - check interaction with slit corners if appropriate
        for p2 in [SLIT_TOP, SLIT_BOTTOM]:
            d = particle.distance_to(p2)
            if d <= R:
                dest.append((p2, d))
    else:
        # No - check interaction with middle wall horizontally
        if abs(particle.x - WIDTH/2) <= R:
            dest.append((Particle(x=WIDTH / 2, y=particle.y, mass=math.inf, is_fake=True), abs(particle.x - WIDTH / 2)))


def lennard_jones_force(r):
    """Calculate lennard jones force for two particles separated by r"""
    assert (r != 0)
    return (12 * EPSILON / R_M) * (((R_M / r) ** 13) - ((R_M / r) ** 7))


def calculate_force(particle, neighbors):
    """Calculate total force exerted on particle by neighbors with the lennard jones force"""
    force_x = 0
    force_y = 0
    for neighbor, _ in neighbors:
        if neighbor != particle:
            # Check if the neighbor particle is not in the same compartment as the original particle
            if not neighbor.is_fake and compartment(particle) != compartment(neighbor):
                # TODO hacer lo de Barto de la pendiente para ver si se ven las partículas entre la ranura
                continue

            # Calculate total force magnitude
            dist = particle.distance_to(neighbor)
            force = lennard_jones_force(dist)
            # Calculate angle between neighbor and particle
            angle = math.atan2(particle.y-neighbor.y, particle.x-neighbor.x)
            # Project the force on each axis component
            force_x += force * math.cos(angle)
            force_y += force * math.sin(angle)
    return force_x, force_y


def recalculate_fp(particles):
    """Calculate the particle ratio on each side"""
    left = 0
    right = 0
    for particle in particles:
        if particle.position.x <= WIDTH / 2:
            left += 1
        else:
            right += 1
    fp_left = left / NUM_PARTICLES
    fp_right = right / NUM_PARTICLES
    return fp_left, fp_right


def potential_energy(particle, neighbors):
    """Calculate potential energy for particle"""

    potential = 0
    for neighbor, dist in neighbors:
        if neighbor != particle:
            potential += EPSILON*((R_M/dist)**12 - 2*(R_M/dist)**6)
    return potential


def compartment(particle):
    """Return which compartment the specified particle is in. 0 for left, 1 for exact middle, 2 for right."""
    if particle.x == WIDTH / 2:
        return 1
    return 0 if particle.x < WIDTH / 2 else 2


def velocity_histogram(particles, filename):
    """Save a histogram with the velocity distribution for particles"""
    # Used for 2.4
    if args['verbose']:
        print("Generating velocity histogram")
    velocities = list()
    for p in particles:
        velocities.append(p.velocity.magnitude())
    plt.clf()
    plt.hist(np.array(velocities), bins=np.arange(np.min(velocities)-1, np.max(velocities)+1, 0.25), histtype='bar',
             color="orange", align="left", linestyle="solid", edgecolor='black', linewidth=0.8)
    plt.title("Frecuencia de las velocidades")
    plt.xlabel("Velocidad")
    plt.ylabel("Frecuencia")
    plt.savefig(filename)

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
SLIT_TOP = Particle(WIDTH/2, HEIGHT/2 + SLIT_SIZE/2, mass=math.inf, is_fake=True)
SLIT_BOTTOM = Particle(WIDTH/2, HEIGHT/2 - SLIT_SIZE/2, mass=math.inf, is_fake=True)

t_accum = 0
fp_left = 1
t = 0
middle_histogram = False

velocity_histogram(particles, "initial_velocity_histogram.jpg")


while fp_left > 0.5:

    if fp_left < 0.75 and not middle_histogram:
        # Generate a histogram when one fourth of the particles have passed to the right side
        velocity_histogram(particles, "middle_velocity_histogram.jpg")
        middle_histogram = True

    # Calculate all neighbors for all particles
    neighbors = CellIndexMethod(particles, radius=R, width=WIDTH, height=HEIGHT).neighbors

    # Initialize variables
    total_mass = 0
    total_velocity = 0
    e_u, e_k = 0, 0
    new_positions, new_velocities = [], []
    for p in particles:
        # Accumulate system energies (do this before adding fake wall particles since those aren't part of the system)
        e_u += potential_energy(p, neighbors[p.id])
        e_k += 0.5 * p.mass * (p.velocity.magnitude() ** 2)

        # Add fake particles to represent walls
        add_wall_neighbors(p, neighbors[p.id])

        # Calculate total force exerted on p
        force_x, force_y = calculate_force(p, neighbors[p.id])
        force = Vector2(force_x, force_y)

        # Calculate new position and velocity using Verlet
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

        # Save positions
        colors = [(255, 255, 255)] * NUM_PARTICLES
        colors += [(0, 255, 0)] * len(fake_particles)
        FileWriter.export_positions_ovito(particles + fake_particles, t, colors=colors, mode="w" if t == 0 else "a", output="output2.txt")

        # Save kinetic and potential energy for current time
        # Used for 2.2
        file = open("energy2.txt", "w" if t == 0 else "a")
        file.write("%g,%g,%g\n" % (t, e_k, e_u))
        file.close()

        # Save fp proportion on the left side of the compartment
        # Used for 2.3
        file = open("fpleft2.txt", "w" if t == 0 else "a")
        file.write("%g,%g\n" % (t, fp_left))
        file.close()

        # Reset counter
        t_accum = 0

    # Evolve particles
    for i in range(len(particles)):
        particles[i].position = new_positions[i]
        particles[i].velocity = new_velocities[i]

    # Recalculate particle proportion on each compartment
    fp_left, _ = recalculate_fp(particles=particles)

    # Add delta t to total time
    t += delta_t

# Generate a histogram for the particle velocity distribution at the end
velocity_histogram(particles, "final_velocity_histogram2.jpg")
