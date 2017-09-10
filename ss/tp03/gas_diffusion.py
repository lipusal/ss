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

if arguments.time:
    import ss.util.timer

# Box dimensions (meters)
height = 0.09
width = 0.24
aperture_width = 0.006


def get_compartment(particle):
    """Return which compartment the specified particle is in. 0 for left, 1 for exact middle, 2 for right."""
    if particle.x == width / 2:
        return 1

    return 0 if particle.x < width / 2 else 2


def time_to_border_wall_collision(particle):
    """Calculate time for the given particle to collide against any border wall. Return infinity if particle will not
    collide with a wall (e.g. if Vx = Vy = 0)."""

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


def time_to_middle_wall_collision(particle):
    """Calculate time for the given particle to collide against the middle wall, taking in consideration the aperture
    size. Return infinity if particle will not collide with middle wall, or if particle will go through aperture."""

    compartment = get_compartment(particle)
    # Get time for particle to reach middle wall in X
    if compartment == 0:
        if particle.velocity.x <= 0:
            return math.inf  # Will collide against a wall first (or is not moving in X)
        time = (width / 2 - particle.radius - particle.position.x) / particle.velocity.x
    elif compartment == 2:
        if particle.velocity.x >= 0:
            return math.inf
        time = (width / 2 + particle.radius - particle.position.x) / particle.velocity.x
    else:
        return math.inf  # Should only happen when inside the aperture

    new_y = particle.position.y + particle.velocity.y * time
    if (height / 2) - (aperture_width / 2) + particle.radius <= new_y <= (height / 2) + (
        aperture_width / 2) - particle.radius:
        # Particle will go through aperture
        return math.inf

    return time


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
        print("WARNING: %s and %s overlap, giving a negative collision time. Ignoring and returning infinity, "
              "make sure particles are not generated with overlap!" % (particle1, particle2))
        return math.inf

    return -(v_r + math.sqrt(d)) / v2


def all_min_collision_times(particles):
    """Return a dictionary of the form (particle_id, (particle, min_collision_time, collision_target)). That is, for
    each particle, save its ID as key, and as value store the Particle itself, the minimum time for it to collide
    against a wall or a particle, and against what it will collide at that time (None for walls and Particles for other
    particles)."""

    result = dict()
    for me in particles:
        # Get the time until this particle first collides against a wall or against another particle. Always need to
        # compare with all other particles because it is not necessarily true that
        # time_to_collision(x, y) == time_to_collision(y, x)
        collision_time, target = min_collision_time(me, particles)
        result[me.id] = (me, collision_time, target)

    return result


def min_collision_time(self, other_particles):
    """For the given particle self, return a tuple of the form (min_collision_time, target), where min_collision_time is
    a float and target is a particle in other_particles, or None if self will first collide against a wall."""

    border_wall_time = time_to_border_wall_collision(self)
    middle_wall_time = time_to_middle_wall_collision(self)
    particle_time = math.inf
    other_particle = None

    for particle in other_particles:
        if particle == self:
            continue

        t = time_to_particle_collision(self, particle)
        if t < particle_time:
            particle_time = t
            other_particle = particle

    min_time = min(border_wall_time, middle_wall_time, (particle_time or math.inf))
    if min_time == border_wall_time:
        # Contemplates the (very rare) case in which a particle will never collide against anything, will insert
        # (math.inf, None). Ignores cases in which a particle collides against a wall and another particle at the
        # same time; takes only the wall collision
        return border_wall_time, None
    elif min_time == middle_wall_time:
        future_self = Particle(self.x, self.y, self.radius, self.mass, self.velocity, self.vel_angle(), True, self)
        future_self.move(self.velocity.x * middle_wall_time, self.velocity.y * middle_wall_time)
        if future_self.distance_to(aperture_top_particle) == 0:
            # Colliding against top aperture border
            return middle_wall_time, aperture_top_particle
        elif future_self.distance_to(aperture_bottom_particle) == 0:
            # Colliding against bottom aperture border
            return middle_wall_time, aperture_bottom_particle
        else:
            # Colliding against middle wall
            return middle_wall_time, None
    else:
        return particle_time, other_particle


def next_collision(data):
    """Get the minimum collision time of all times in the specified data, where data has the form of what is returned
    by #min_collision_times. Return (particle, min_time, target)"""

    result = None
    min_time = math.inf

    for particle_id, (particle, time, target) in data.items():
        if time < min_time:
            min_time = time
            result = (particle, min_time, target)
        elif time == min_time and result is not None and particle_id != result[2].id:
            # Two collisions at the same time with different pairs of particles (otherwise particle_id == result[2].id)
            print("***************************************************************************************************")
            print("WARNING!!!! Found two collisions at the same time: %s <-> %s and %s <-> %s. Do we get to go to "
                  "Jamaica?" % (result[0], result[2], particle, target))
            print("No but seriously, ignoring second collision. If this happens a lot, consider contemplating "
                  "multiple collisions!")
            print("***************************************************************************************************")

    return result


def evolve_particles(particles, time, colliding_particle, target):
    for particle in particles:

        # Move particle
        particle.move(particle.velocity.x * time, particle.velocity.y * time)

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

    # Particles moved, simulate collisions
    if target is None:
        wall_collision(colliding_particle)
    else:
        particle_collision(colliding_particle, target)


def wall_collision(particle):
    # When the particle crashes into a wall, one of its velocity's components should change direction (both if crashing
    # against a corner)

    # Middle wall
    if (width / 2) - particle.radius <= particle.x <= (width / 2) + particle.radius:
        particle.velocity.x *= -1
        return

    # Border walls
    if particle.y >= height - particle_radius or particle.y <= 0 + particle_radius:
        particle.velocity.y *= -1
    if particle.x >= width - particle_radius or particle.x <= 0 + particle_radius:
        particle.velocity.x *= -1


def particle_collision(particle1, particle2):
    # Filmina 20 de teórica 3
    delta_r = particle2.position - particle1.position
    delta_v = particle2.velocity - particle1.velocity
    o = particle1.radius + particle2.radius

    j = 2 * particle1.mass * particle2.mass * delta_v.dot(delta_r) / (o * (particle1.mass + particle2.mass))
    j_x = j * delta_r.x / o
    j_y = j * delta_r.y / o

    particle1.velocity.x += j_x / particle1.mass
    particle1.velocity.y += j_y / particle1.mass

    particle2.velocity.x -= j_x / particle2.mass
    particle2.velocity.y -= j_y / particle2.mass


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
particle_radius = 0.0015
particle_mass = 1.0
particles = list()
# Particles for aperture borders, needed for more realistic collisions
aperture_top_particle = Particle(width / 2, (height / 2) + (aperture_width / 2) - particle_radius, radius=0, mass=math.inf,
                                 v=0, o=0, is_fake=True)
aperture_bottom_particle = Particle(width / 2, (height / 2) - (aperture_width / 2) + particle_radius, radius=0, mass=math.inf, v=0, o=0,
                                    is_fake=True)
# colors = list()

# Fake middle wall particles for visualization
y = 0.0
fake_particles = list()
while y <= height:
    if not height/2 - aperture_width/2 + particle_radius < y < height/2 + aperture_width/2 - particle_radius:
        fake_particles.append(Particle(width/2, y, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
    y += particle_radius

fake_particles.append(Particle(0, 0, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
fake_particles.append(Particle(width, 0, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
fake_particles.append(Particle(0, height, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
fake_particles.append(Particle(width, height, radius=0, mass=math.inf, v=0, o=0, is_fake=True))

# Create particles
for particle_count in range(arguments.n):
    new_particle = Particle.get_random_particle(max_height=height, max_width=width / 2 - particle_radius,
                                                radius=particle_radius, speed=particle_velocity, mass=particle_mass)

    done = False
    while not done:
        overlap = False
        # Make sure the new particle doesn't overlap with any other existing particle
        for existing_particle in particles:
            if new_particle.distance_to(existing_particle) < 0:
                overlap = True
                new_particle = Particle.get_random_particle(max_height=height, max_width=width / 2 - particle_radius,
                                                            radius=particle_radius, speed=particle_velocity,
                                                            mass=particle_mass)
                break

        done = not overlap

    particles.append(new_particle)
    # Color particles according to initial direction
    # colors.append(radians_to_rgb(new_particle.vel_angle()))

t = 0

# while fp_left > 0.5:
for i in range(1000):
    if arguments.verbose:
        print("Processing frame #%i" % i)

    collision_times = all_min_collision_times(particles)
    colliding_particle, min_time, target = next_collision(collision_times)

    # Subtract min_time from all collision times; colliding particle(s) will have their collision time set to 0
    for particle_id, (particle, time, target2) in collision_times.items():
        collision_times[particle_id] = (particle, time - min_time, target2)

    evolve_particles(particles, min_time, colliding_particle, target)

    # Update next collision of collided particle(s), and any other particles they may now collide with
    for particle in [colliding_particle, target]:
        if particle is not None:
            next_collision_time, next_target = min_collision_time(particle, particles)
            collision_times[particle.id] = (particle, next_collision_time, next_target)

            # If next collision is with another particle, and if it will now happen sooner than when that other particle
            # was going to collide before, also update that particle's collision time
            if next_target is not None and next_collision_time < collision_times[next_target.id][1]:
                collision_times[next_target.id] = (next_target, next_collision_time, particle)

    t += min_time
    recalculate_fp()

    # Color the collided particle(s) red and blue
    colors = [(255, 255, 255)] * arguments.n
    for j in range(len(particles)):
        if particles[j] == colliding_particle:
            colors[j] = (255, 0, 0)
        elif target is not None and particles[j] == target:
            colors[j] = (0, 0, 255)

    # Color the fake middle wall particles green
    colors += [(0, 255, 0)] * len(fake_particles)

    FileWriter.export_positions_ovito(particles + fake_particles, t=t, colors=colors, output=arguments.output,
                                      mode='w' if i == 0 else 'a')
