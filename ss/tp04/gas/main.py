import math
import random

import numpy as np
from euclid3 import Vector2

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
WIDTH = 400     # Area width. Each compartment has width WIDTH/2 [dimensionless]
HEIGHT = 200    # Area height [dimensionless]
SLIT_SIZE = 10  # [dimensionless]
NUM_PARTICLES = 1000
# Guard to make sure all particles are at least this distance from each other
# TODO: Have program work without min_distance = 0
MIN_DISTANCE = 0.5

fp = 1          # particles on left compartment / total particles (ie. all particles start on the left compartment)

# TODO parametrizar tiempo y delta_t
TIME = 1000
MAX_TIME = 0.1
delta_t = 0.00003
PARTICLE_RADIUS = 0

def generate_random_particles():
    """Create particles with random positions in the box"""

    # Fake middle wall particles for visualization
    y = 0.0
    fake_particles = list()
    while y <= HEIGHT:
        if not HEIGHT / 2 - SLIT_SIZE / 2 + PARTICLE_RADIUS < y < HEIGHT / 2 + SLIT_SIZE / 2 - PARTICLE_RADIUS:
            fake_particles.append(Particle(WIDTH / 2, y, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
        y += 1

    fake_particles.append(Particle(0, 0, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
    fake_particles.append(Particle(WIDTH, 0, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
    fake_particles.append(Particle(0, HEIGHT, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
    fake_particles.append(Particle(WIDTH, HEIGHT, radius=0, mass=math.inf, v=0, o=0, is_fake=True))

    # Real particles
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
                    new_particle = Particle.get_random_particle(max_height=HEIGHT,
                                                                max_width=WIDTH / 2 - PARTICLE_RADIUS,
                                                                radius=PARTICLE_RADIUS, speed=V0, mass=M,
                                                                min_height=MIN_DISTANCE, min_width=MIN_DISTANCE)
                    break

            done = not overlap

        result.append(new_particle)

    if args['verbose']:
        print("done")

    return result, fake_particles


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
        dest.append((Particle(x=WIDTH, y=particle.y, mass=math.inf, is_fake=True), particle.x))

    # Check if there is interaction with the top wall
    if HEIGHT - particle.y <= R:
        dest.append((Particle(x=particle.x, y=HEIGHT, mass=math.inf, is_fake=True), particle.y))

    # Check if there is interaction with the middle wall
    if (particle.y > HEIGHT/2 + SLIT_SIZE/2 or particle.y < HEIGHT/2 - SLIT_SIZE/2) and abs(particle.x - WIDTH/2) <= R:
        dest.append(
            (Particle(x=WIDTH / 2, y=particle.y, mass=math.inf, is_fake=True), abs(particle.x - WIDTH/2)))

def lennard_jones_force(r):
    assert (r != 0)
    return (12 * EPSILON / R_M) * (((R_M / r) ** 13) - ((R_M / r) ** 7))


def calculate_force(particle, neighbors):
    """Calculate total force exerted on particle by neighbors with the lennard jones force"""
    force_x = 0
    force_y = 0
    for neighbor, _ in neighbors:
        if neighbor != particle:
            dist = particle.distance_to(neighbor)
            force = lennard_jones_force(dist)
            angle = math.atan2(particle.y-neighbor.y, particle.x-neighbor.x)
            force_x += force * math.cos(angle)
            force_y += force * math.sin(angle)

    return force_x, force_y

# TODO
def write_fake_particles():
    return

# ----------------------------------------------------------------------------------------------------------------------
#       MAIN
# ----------------------------------------------------------------------------------------------------------------------
if args['time']:
    import ss.util.timer

# Generate random particles
particles, fake_particles = generate_random_particles()

# TODO used for debugging
for p in particles:
    if p.x > WIDTH or p.x < 0 or p.y > HEIGHT or p.y < 0:
        raise Exception("Generated particle %s is out of bounds" %p)

# Load particles from file
# from ss.util.file_reader import FileReader
# positions, properties = FileReader.import_positions_ovito("D:\\Users\\juan_\\Documents\\PycharmProjects\\ss\\ex\\04\\dynamic.txt", frame=1)
# particles = load_particles(positions, properties)

for t in np.arange(0, MAX_TIME, delta_t):
    print("Processing t=%f..." % t)

    neighbors = CellIndexMethod(particles, radius=R, width=WIDTH, height=HEIGHT).neighbors
    # TODO: Cell Index Method va a hacer que dos partículas separadas por la pared del medio interactúen (si están a
    # TODO: menos de R) pero el profesor dijo que no hacía falta contemplar eso. Para calculate_force habría que filtrar
    # TODO: esos casos


    total_mass = 0
    total_velocity = 0
    new_positions, new_velocities = [], []
    for p in particles:
        add_wall_neighbors(p, neighbors[p.id])
        # Calculate total force exerted on p
        force_x, force_y = calculate_force(p, neighbors[p.id])
        force = Vector2(force_x, force_y)
        # Calculate new position and velocity using Verlet
        # TODO: usar otros?
        new_position = verlet.r(particle=p, delta_t=delta_t, force=force)
        # # Debugging Juan
        # if new_position.x < 0 or new_position.y < 0 or new_position.x > WIDTH or new_position.y > HEIGHT:
        #     if abs(force_x) > 10 or abs(force_y) > 10:
        #         force_x, force_y = calculate_force(p, neighbors[p.id])
        #     new_position = verlet.r(particle=p, delta_t=delta_t, force=force)

        new_positions.append(new_position)
        new_velocity = verlet.v(p, delta_t, force)
        new_velocities.append(new_velocity)
        total_mass += p.mass
        total_velocity += new_velocity.magnitude()

        # TODO remove, used for debugging
        if new_position.x < 0 or new_position.y < 0 or new_position.x > WIDTH or new_position.y > HEIGHT:
            raise Exception("The particle moved out of the bounds, x:%f y:%f, width: %f, height: %f" %(new_position.x, new_position.y, WIDTH, HEIGHT))

    # Debugging Juan
    delta_positions = [abs(new_positions[i] - particles[i].position) for i in range(len(particles))]
    min_d, max_d = min(delta_positions), max(delta_positions)

    # Evolve particles
    for i in range(len(particles)):
        particles[i].position = new_positions[i]
        particles[i].velocity = new_velocities[i]
    colors = [(255, 255, 255)]*NUM_PARTICLES
    colors += [(0, 255, 0)] * len(fake_particles)
    FileWriter.export_positions_ovito(particles + fake_particles, t, colors=colors, mode="w" if t == 0 else "a")

    # Write total energy in iteration
    k = 0.5 * total_mass * total_velocity**2
    file = open("kinetic_energy.txt", "w" if t == 0 else "a")
    file.write("%i\t%g\n" % (t, k))
    file.close()