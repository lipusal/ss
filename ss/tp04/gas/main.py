import math

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

fp = 1          # particles on left compartment / total particles (ie. all particles start on the left compartment)

# TODO parametrizar tiempo y delta_t
TIME = 1000
delta_t = 0.0001
PARTICLE_RADIUS = 0


def lennard_jones_force(r):
    assert (r != 0)
    return (12 * EPSILON / R_M) * (((R_M / r) ** 13) - ((R_M / r) ** 7))


def generate_particles():
    """Create particles with random positions in the box"""

    result = list()

    if args['verbose']:
        print("Generating %i particles without overlap..." % NUM_PARTICLES, end='', flush=True)

    for particle_count in range(NUM_PARTICLES):
        new_particle = Particle.get_random_particle(max_height=HEIGHT, max_width=WIDTH / 2 - PARTICLE_RADIUS,
                                                    radius=PARTICLE_RADIUS, speed=V0, mass=M)
        done = False
        while not done:
            overlap = False
            # Make sure the new particle doesn't overlap with any other existing particle
            for existing_particle in result:
                if new_particle.distance_to(existing_particle) < 0:
                    overlap = True
                    new_particle = Particle.get_random_particle(max_height=HEIGHT,
                                                                max_width=WIDTH / 2 - PARTICLE_RADIUS,
                                                                radius=PARTICLE_RADIUS, speed=V0, mass=M)
                    break

            done = not overlap

        result.append(new_particle)

    if args['verbose']:
        print("done")

    return result


def add_wall_neighbors(particle, dest):
    """Add fake particles that will represent the wall particles that exert force on the particle"""

    # Check if there is interaction with the left wall
    if particle.x <= R:
        dest.append((Particle(x=0, y=particle.y, mass=math.inf, is_fake=True), particle.x))

    # Check if there is interaction with the bottom wall
    if particle.y <= R:
        dest.append((Particle(x=particle.y, y=0, mass=math.inf, is_fake=True), particle.y))

    # Check if there is interaction with the right wall
    if WIDTH - particle.x <= R:
        dest.append((Particle(x=WIDTH, y=particle.y, mass=math.inf, is_fake=True), particle.x))

    # Check if there is interaction with the top wall
    if HEIGHT - particle.y <= R:
        dest.append((Particle(x=particle.x, y=HEIGHT, mass=math.inf, is_fake=True), particle.y))

    # Check if there is interaction with the middle wall
    if particle.y > HEIGHT/2 + SLIT_SIZE/2 or particle.y < HEIGHT/2 - SLIT_SIZE/2 and abs(particle.x - WIDTH/2) <= R:
        dest.append(
            (Particle(x=WIDTH / 2, y=particle.y, mass=math.inf, is_fake=True), abs(particle.x - WIDTH/2)))


def calculate_force(particle, neighbors):
    """Calculate total force exerted on particle by neighbors with the lennard jones force"""
    force_x = 0
    force_y = 0
    for neighbor, _ in neighbors:
        if neighbor != particle:
            dist_x = abs(particle.x - neighbor.x)
            # If they are aligned there will only be one force component
            if dist_x != 0:
                force_x += lennard_jones_force(dist_x)
            dist_y = abs(particle.y - neighbor.y)
            # If they are aligned there will only be one force component
            if dist_y != 0:
                force_y += lennard_jones_force(dist_y)
    return force_x, force_y


# ----------------------------------------------------------------------------------------------------------------------
#       MAIN
# ----------------------------------------------------------------------------------------------------------------------
if args['time']:
    import ss.util.timer

# Generate random particles
particles = generate_particles()

for t in np.arange(0, 1, delta_t):
    neighbors = CellIndexMethod(particles, radius=R, width=WIDTH, height=HEIGHT).neighbors
    # TODO: Cell Index Method va a hacer que dos partículas separadas por la pared del medio interactúen (si están a
    # TODO: menos de R) pero el profesor dijo que no hacía falta contemplar eso. Para calculate_force habría que filtrar
    # TODO: esos casos

    for p in particles:
        add_wall_neighbors(p, neighbors[p.id])
        # Calculate total force exerted on p
        force_x, force_y = calculate_force(p, neighbors[p.id])
        force = Vector2(force_x, force_y)
        # Calculate new position and velocity using Verlet
        # TODO: usar otros?
        new_position = verlet.r(particle=p, delta_t=delta_t, force=force)
        p.position = new_position
        new_velocity = verlet.v(p, delta_t, force)
        p.velocity = new_velocity

    FileWriter.export_positions_ovito(particles, t, mode="w" if t == 0 else "a")
