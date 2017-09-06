import random
import math

import ss.util.args as args
from ss.cim.particle import Particle
from ss.util.file_writer import FileWriter

args.parser.description = "Self-propulsed particles program. Simulates particles with a (random) given velocity that" \
                          "changes over time, and whose change is influenced by other particles within a radius"
args.parser.add_argument("-n", help="Amount of particles", type=int, default=3)
arguments = args.parse_args()

# Box dimensions
height = 0.09
width = 0.24

def calculate_collision_times(min_collision_times):

    # TODO ver donde estan las paredes, esta muy hardcodeado el width y el 0! y donde hay ranuras y otras particulas

    for particle in particles:

        # Calculate minimum collision time in x axis
        if particle.velocity.x >= 0:
            collision_time_x = (width - particle.radius - particle.position.x) / particle.velocity.x
        elif particle.velocity.x < 0:
            collision_time_x = (0 + particle.radius - particle.position.x) / particle.velocity.x

        # Calculate minimum collision time in y axis
        if particle.velocity.y >= 0:
            collision_time_y = (height - particle.radius - particle.position.y) / particle.velocity.y
        elif particle.velocity.y < 0:
            collision_time_y = (0 + particle.radius - particle.position.y) / particle.velocity.y

        # Set minimum time for collision on either axis
        min_collision_times[particle.id] = min(collision_time_x, collision_time_y)

        if(min_collision_times[particle.id] < 0):
            raise ValueError('Collision time should never be a negative value')

def evolve_particles(time):

    for particle in particles:
        particle.move_to(particle.x + (particle.velocity.x * time), particle.y + (particle.velocity.y * time))

        # When the particle crashes into a wall the velocity should change direction
        #if particle.y +  particle_radius + (particle.velocity.y * time) >= height:

        if particle.y >= height - particle_radius:
            particle.velocity.y = - particle.velocity.y
            # y_displacement = (particle.velocity.y * time) - 2((height-particle.y) - particle_radius)
            # particle.position.y -= y_displacement

        # elif particle.y - particle_radius - (particle.velocity.y * time) <= 0:

        elif particle.y <= 0 + particle_radius:
            particle.velocity.y = - particle.velocity.y
            # y_displacement = (particle.velocity.y * time) - 2(particle.position.y - particle_radius)
            # particle.position.y += y_displacement

        # elif particle.x + particle_radius + (particle.velocity.x * time) >= width:
        elif particle.x  >= width - particle_radius:
            particle.velocity.x = - particle.velocity.x
            # x_displacement = (particle.velocity.x * time) - 2((width - particle.x) - particle_radius)
            # particle.position.x -= x_displacement

        # elif particle.x - particle_radius - (particle.velocity.x * time) <= 0:
        elif particle.x  <= 0 + particle_radius:
            particle.velocity.x = - particle.velocity.x
            # x_displacement = (particle.velocity.x * time) - 2(particle.x - particle_radius)
            # particle.position.x -= x_displacement

        # Raise an exception when the particle is outside the board limits
        if particle.y > height:
            raise ValueError('The position of the particle cannot be outside the box, the y position must be smaller than the height')
        if particle.x > width:
            raise ValueError('The position of the particle cannot be outside the box, the x position must be smaller than the width')
        if particle.x < 0:
            raise ValueError('The position of the particle cannot be outside the box, the x position must be more than 0')
        if particle.y < 0:
            raise ValueError('The position of the particle cannot be outside the box, the y position must be more than 0')

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
colors = list()
for particle_count in range(arguments.n):
    x = random.uniform(particle_radius, (width / 2) - particle_radius)
    y = random.uniform(particle_radius, height - particle_radius)
    o = random.uniform(0.0, 2 * math.pi)
    particles.append(Particle(x, y, particle_radius, particle_mass, particle_velocity, o))
    colors.append((255, 255, particle_count * 5))

#while fp_left > 0.5:
for i in range(50):
    # TODO: cambiar solo los que iban a chocar con algo que choco no fuerza bruta a lo loco
    min_collision_times = dict()
    calculate_collision_times(min_collision_times)
    min_time = min(min_collision_times.values())
    evolve_particles(min_time)
    # recalculate_fp()
    FileWriter.export_positions_ovito(particles, t=i, colors=colors, output=("output.txt"), mode='w' if i == 0 else 'a')
