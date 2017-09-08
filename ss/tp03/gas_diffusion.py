import random
import math

import ss.util.args as args
from ss.cim.particle import Particle
from ss.util.file_writer import FileWriter
from ss.util.colors import radians_to_rgb

# TODO: Update description
args.parser.description = "Self-propulsed particles program. Simulates particles with a (random) given velocity that" \
                          "changes over time, and whose change is influenced by other particles within a radius"
args.parser.add_argument("-n", help="Amount of particles", type=int, default=20)
arguments = args.parse_args()

# Box dimensions (meters)
height = 0.09
width = 0.24


def calculate_collision_times(min_collision_times):
    # TODO ver donde estan las paredes, esta muy hardcodeado el width y el 0! y donde hay ranuras y otras particulas

    for particle in particles:

        # Calculate minimum collision time in x axis
        if particle.velocity.x > 0:
            collision_time_x = (width - particle.radius - particle.position.x) / particle.velocity.x
        elif particle.velocity.x < 0:
            collision_time_x = (0 + particle.radius - particle.position.x) / particle.velocity.x
        else:
            collision_time_x = math.inf

        # Calculate minimum collision time in y axis
        if particle.velocity.y > 0:
            collision_time_y = (height - particle.radius - particle.position.y) / particle.velocity.y
        elif particle.velocity.y < 0:
            collision_time_y = (0 + particle.radius - particle.position.y) / particle.velocity.y
        else:
            collision_time_y = math.inf

        # Set minimum time for collision on either axis
        # TODO: Mark that particle will collide with wall, i.e. None?
        min_collision_times[particle.id] = min(collision_time_x, collision_time_y)

        # Raise an exception when the collision time is negative
        if min_collision_times[particle.id] < 0:
            raise ValueError('Collision time should never be a negative value')


def evolve_particles(time):
    for particle in particles:

        # Move particle
        particle.move(particle.velocity.x * time, particle.velocity.y * time)

        # When the particle crashes into a wall, one of its velocity's components should change direction
        if particle.y >= height - particle_radius or particle.y <= 0 + particle_radius:
            particle.velocity.y *= -1
        elif particle.x >= width - particle_radius or particle.x <= 0 + particle_radius:
            particle.velocity.x *= -1

        # TODO ver que corrobore tambien el tema del radio onda que la posicion no sea 0.5 cuando el radio es 1.

        # Raise an exception when the particle is outside the board limits

        # This can be simplified by changing >=, <=, etc. above to just ==, and adding else: "Outside of board".
        # However, it won't say which side the particle is out from
        if particle.y > height:
            raise ValueError(
                'The position of the particle cannot be outside the box, the y position must be smaller than the height')
        if particle.x > width:
            raise ValueError(
                'The position of the particle cannot be outside the box, the x position must be smaller than the width')
        if particle.x < 0:
            raise ValueError(
                'The position of the particle cannot be outside the box, the x position must be more than 0')
        if particle.y < 0:
            raise ValueError(
                'The position of the particle cannot be outside the box, the y position must be more than 0')


# Particle ratio on each side of the box
fp_left = 1
fp_right = 0


def recalculate_fp():
    global fp_left
    global fp_right
    left = 0
    right = 0
    for particle in particles:
        if particle.position.x <= width / 2:
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
    # TODO dividir width por dos para que este en la mitad de la caja
    x = random.uniform(particle_radius, width - particle_radius)
    y = random.uniform(particle_radius, height - particle_radius)
    o = random.uniform(0.0, 2 * math.pi)
    particles.append(Particle(x, y, particle_radius, particle_mass, particle_velocity, o))
    # TODO: Consider making Ovito color particles so we don't have to recalculate colors all the time
    colors.append(radians_to_rgb(o))

# while fp_left > 0.5:
t = 0
for i in range(500):
    # TODO: cambiar solo los que iban a chocar con algo que choco no fuerza bruta a lo loco
    min_collision_times = dict()
    calculate_collision_times(min_collision_times)
    min_time = min(min_collision_times.values())
    evolve_particles(min_time)
    t += min_time
    recalculate_fp()
    FileWriter.export_positions_ovito(particles, t=t, colors=colors, output=arguments.output,
                                      mode='w' if i == 0 else 'a')
