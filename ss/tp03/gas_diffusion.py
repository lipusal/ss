import random
import math

import ss.util.args as args
from ss.cim.particle import Particle

args.parser.description = "Self-propulsed particles program. Simulates particles with a (random) given velocity that" \
                          "changes over time, and whose change is influenced by other particles within a radius"
args.parser.add_argument("-n", help="Amount of particles", type=int, default=100)
arguments = args.parse_args()

def calculate_collision_times(min_collision_times):
    # TODO ver donde estan las paredes, esta muy hardcodeado el width y el 0! y donde hay ranuras y otras particulas
    # Calculate initial collision time
    for particle in particles:

        # Calculate minimum collision time in x axis
        if particle.velocity.x > 0:
            collision_time_x = (width - particle.radius - particle.position.x) / particle.velocity.x
        elif particle.velocity.x < 0:
            collision_time_x = (0 + particle.radius - particle.position.x) / particle.velocity.x

        # Calculate minimum collision time in y axis
        if particle.velocity.y > 0:
            collision_time_y = (height - particle.radius - particle.position.y) / particle.velocity.y
        elif particle.velocity.y < 0:
            collision_time_y = (0 + particle.radius - particle.position.y) / particle.velocity.y

        # Set minimum time for collision on either axis
        min_collision_times[particle.id] = min(collision_time_x, collision_time_y)


def evolve_particles(time):

    for particle in particles:
        particle.position.x += particle.velocity.x * time
        particle.position.y += particle.velocity.y * time

# Box dimensions
height = 0.09
width = 0.24

# Particle ratio on each side of the box
fp_left = 1
fp_right = 0

def recalculate_fp():
    global fp_left
    global fp_right
    left = 0
    right = 0
    for particle in particles:
        if particle.position.x <= width/2:
            left += 1
        else:
            right += 1
    fp_left = left / arguments.n
    fp_right = right / arguments.n


# Generate particles with random velocity direction
particle_velocity = 0.01
particle_radius = 0.006
particle_mass = 1.0
particles = list()
for particle_count in range(arguments.n):
    x = random.uniform(0.0, width / 2)
    y = random.uniform(0.0, height)
    o = random.uniform(0.0, 2 * math.pi)
    particles.append(Particle(x, y, particle_radius, particle_mass, particle_velocity, o))



min_collision_times = list()

while fp_left > 0.5:
    calculate_collision_times(min_collision_times)
    min_time = min(min_collision_times)
    evolve_particles(min_time)
    recalculate_fp()
    print(fp_left)


