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


def time_to_wall_collision(particle):
    """Calculate time for the given particle to collide against any wall. Return infinity if particle will not collide
    with a wall (e.g. if Vx = Vy = 0)."""
    # TODO: Return which wall the collision will be with?
    # TODO ver donde estan las paredes, esta muy hardcodeado el width y el 0! y donde hay ranuras y otras particulas

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
    result = min(collision_time_x, collision_time_y)
    if result < 0:
        raise ValueError('Collision time should never be a negative value')

    return result


def time_to_particle_collision(particle1, particle2):
    """Calculate time for the two given particles to collide. Return infinity if they will not collide."""

    delta_r = particle2.position - particle1.position
    delta_v = particle2.velocity - particle1.velocity
    v_r = delta_v.dot(delta_r)

    if v_r >= 0:
        return math.inf

    o = particle1.radius + particle2.radius
    v2 = delta_v.dot(delta_v)
    d = (v_r ** 2) - v2 * (delta_r.dot(delta_r) - (o ** 2))
    if d < 0:
        return math.inf

    result = -(v_r + math.sqrt(d)) / v2
    if result < 0:
        # TODO: Make sure particles are not generate with overlap
        print("WARNING: %s and %s overlap, giving a negative collision time. Ignoring and returning infinity, "
              "make sure particles are not generated with overlap!" % (particle1, particle2))
        return math.inf

    return -(v_r + math.sqrt(d)) / v2


def min_collision_times(particles):
    """Returns a dictionary of the form (particle_id, (min_collision_time, collision_target)). That is, for each
    particle, the minimum time for it to collide against a wall or a particle, and against what it will collide at that
    time."""

    result = dict()
    for i in range(len(particles) - 1):
        me = particles[i]
        wall_time = time_to_wall_collision(me)
        particle_time = math.inf
        other_particle = None

        # Get the other particle that this particle will first collide with. Iterate from the next particle to the end;
        # there's no need to loop over all particles again, since time_to_collision(x, y) == time_to_collision(y, x)
        for j in range(i + 1, len(particles)):
            t = time_to_particle_collision(me, particles[j])
            if t < particle_time:
                particle_time = t
                other_particle = particles[j]

        if wall_time <= particle_time or math.inf:
            # Contemplates the (very rare) case in which a particle will never collide against anything, will insert
            # (math.inf, None). Ignores cases in which a particle collides against a wall and another particle at the
            # same time; takes only the wall collision
            # TODO mark against which wall it will collide?
            result[me.id] = (wall_time, None)
        else:
            result[me.id] = (particle_time, other_particle)
            result[other_particle.id] = (particle_time, me)

    return result


def min_collision_time(data):
    """Get the minimum collision time of all times in the specified data, where data has the form of what is returned
    by #min_collision_times. Return (min_time, target)"""
    result = None
    min_time = math.inf

    for particle_id, (time, target) in data.items():
        if time < min_time:
            min_time = time
            result = (min_time, target)

    return result


def evolve_particles(particles, time):
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

t = 0
collision_times = min_collision_times(particles)

# while fp_left > 0.5:
for i in range(500):
    min_time, target = min_collision_time(collision_times)
    evolve_particles(particles, min_time)

    # Subtract min_time from all collision times; colliding particle(s) will have their collision time set to 0
    for particle_id, (time, target) in collision_times.items():
        collision_times[particle_id] = (time - min_time, target)

    t += min_time
    recalculate_fp()
    FileWriter.export_positions_ovito(particles, t=t, colors=colors, output=arguments.output,
                                      mode='w' if i == 0 else 'a')
