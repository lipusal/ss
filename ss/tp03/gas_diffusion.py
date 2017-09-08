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


def all_min_collision_times(particles):
    """Return a dictionary of the form (particle_id, (min_collision_time, collision_target)). That is, for each
    particle, the minimum time for it to collide against a wall or a particle, and against what it will collide at that
    time."""

    result = dict()
    for i in range(len(particles) - 1):
        me = particles[i]

        # Get the other particle that this particle will first collide with. Iterate from the next particle to the end;
        # there's no need to loop over all particles again, since time_to_collision(x, y) == time_to_collision(y, x)
        collision_time, target = min_collision_time(me, particles[i+1:])

        result[me.id] = (collision_time, target)
        if target is not None:
            # If target will collide against a wall before colliding with me, when it gets processed in a following
            # iteration it will overwrite its collision time with the wall's.
            result[target.id] = (collision_time, me)

    return result


def min_collision_time(self, other_particles):
    """For the given particle self, return a tuple of the form (min_collision_time, target), where min_collision_time is
    a float and target is a particle in other_particles, or None if self will first collide against a wall."""

    wall_time = time_to_wall_collision(self)
    particle_time = math.inf
    other_particle = None

    for particle in other_particles:
        if particle == self:
            continue

        t = time_to_particle_collision(self, particle)
        if t < particle_time:
            particle_time = t
            # Find in list, https://stackoverflow.com/a/9542768/2333689
            other_particle = next(x for x in other_particles if x.id == particle.id)

    if wall_time <= particle_time or math.inf:
        # Contemplates the (very rare) case in which a particle will never collide against anything, will insert
        # (math.inf, None). Ignores cases in which a particle collides against a wall and another particle at the
        # same time; takes only the wall collision
        # TODO mark against which wall it will collide?
        return wall_time, None
    else:
        return particle_time, other_particle


def next_collision(data):
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
# colors = list()
for particle_count in range(arguments.n):
    # TODO dividir width por dos para que este en la mitad de la caja

    new_particle = Particle.get_random_particle(max_height=height, max_width=width, radius=particle_radius, speed=particle_velocity)

    # Check if a particle is superposed with another one
    for i in range(len(particles)):
        particle = particles[i]
        if new_particle.distance_to(particle) < particle_radius:
            new_particle = Particle.get_random_particle(max_height=height, max_width=width, radius=particle_radius,
                                                        speed=particle_velocity)
            i=0

    particles.append(new_particle)
    # Color particles according to initial direction
    # colors.append(radians_to_rgb(new_particle.vel_angle()))

t = 0
collision_times = all_min_collision_times(particles)

# while fp_left > 0.5:
for i in range(500):
    min_time, target = next_collision(collision_times)
    evolve_particles(particles, min_time)

    collided_particle = None
    # Subtract min_time from all collision times; colliding particle(s) will have their collision time set to 0
    for particle_id, (time, target) in collision_times.items():
        collision_times[particle_id] = (time - min_time, target)
        if collision_times[particle_id][0] == 0:
            collided_particle = next(x for x in particles if x.id == particle_id)

    # TODO Nati: Simulate collision between wall and collided_particle, or between collided_particle and target

    # Update next collision of collided particle(s), and any other particles they may now collide with
    for particle in [collided_particle, target]:
        if particle is not None:
            next_collision_time, next_target = min_collision_time(particle, particles)
            collision_times[particle.id] = (next_collision_time, next_target)

            # If next collision is with another particle, and if it will now happen sooner than when that other particle
            # was going to collide before, also update that particle's collision time
            if next_target is not None and next_collision_time < collision_times[next_target.id]:
                collision_times[next_target.id] = (next_collision_time, particle)

    t += min_time
    recalculate_fp()

    # Color the collided particle(s) red and blue
    colors = [(255, 255, 255)] * arguments.n
    for j in range(len(particles)):
        if particles[j] == collided_particle:
            colors[j] = (255, 0, 0)
        elif target is not None and particles[j] == target:
            colors[j] = (0, 255, 0)

    FileWriter.export_positions_ovito(particles, t=t, colors=colors, output=arguments.output,
                                      mode='w' if i == 0 else 'a')
