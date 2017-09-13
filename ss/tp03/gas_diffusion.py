import math

import ss.util.args as args
from ss.cim.particle import Particle
from ss.util.file_writer import FileWriter
from ss.util.colors import radians_to_rgb

# TODO: Update description
args.parser.description = "Gas Diffusion simulation Program. Simulates how a number of given gas particles diffuse " \
                          "from one compartment to another through a slit"
args.parser.add_argument("-n", help="Amount of particles", type=int, default=20)
args.parser.add_argument("--aperture", "-a", help="Aperture size (meters), default is 0.006", type=float, default=0.006)
args.parser.add_argument("--radius", "-r", help="Particle radius (meters), default is 0.0015", type=float,
                         default=0.0015)
args.parser.add_argument("--mass", "-k", help="Particle mass (kilograms), default is 1", type=float, default=1)
args.parser.add_argument("--speed", "-s", help="Particle speed (meters per second), default is 0.01", type=float,
                         default=0.001)
args.parser.add_argument("--cutoff", "-f", help="Distribution cutoff. When the left particles/total particles ratio is "
                                                "below the cutoff, simulation will stop. Default is 0.5",
                         type=float, default=0.5)
args.parser.add_argument("--delta", "-d", help="Approximate delta t between rendered frames (seconds). Note that frames"
                                               " may be further apart, but never closer together. Default is 0.5",
                         type=float, default=0.5)

arguments = args.parse_args()

if arguments.time:
    import ss.util.timer

# Constant values
# Box dimensions (meters)
HEIGHT = 0.09
WIDTH = 0.24
# Particle characteristics(m/s, m, kg)))
PARTICLE_SPEED = arguments.speed
PARTICLE_RADIUS = arguments.radius
PARTICLE_MASS = arguments.mass
# Aperture dimensions(meters)
APERTURE_WIDTH = arguments.aperture
# Scientific Constants
K = 1.38 * 10e-26   # Boltzmann Constant

impulse = 0
temperature = 0

#TODO ver si sacar global a juancito probablemente no le guste jeje
aperture_top_particle = None
aperture_bottom_particle = None

######Functions######

def generate_particles():  # Generate particles with random velocity direction
    # Generate particles with random velocity direction

    particles = list()

    global aperture_top_particle
    global aperture_bottom_particle

    # Particles for aperture borders, needed for more realistic collisions
    aperture_top_particle = Particle(WIDTH / 2, (HEIGHT / 2) + (APERTURE_WIDTH / 2) - PARTICLE_RADIUS, radius=0,
                                     mass=math.inf,
                                     v=0, o=0, is_fake=True)
    aperture_bottom_particle = Particle(WIDTH / 2, (HEIGHT / 2) - (APERTURE_WIDTH / 2) + PARTICLE_RADIUS, radius=0,
                                        mass=math.inf, v=0, o=0,
                                        is_fake=True)

    # Fake middle wall particles for visualization
    y = 0.0
    fake_particles = list()
    while y <= HEIGHT:
        if not HEIGHT / 2 - APERTURE_WIDTH / 2 + PARTICLE_RADIUS < y < HEIGHT / 2 + APERTURE_WIDTH / 2 - PARTICLE_RADIUS:
            fake_particles.append(Particle(WIDTH / 2, y, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
        y += PARTICLE_RADIUS

    fake_particles.append(Particle(0, 0, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
    fake_particles.append(Particle(WIDTH, 0, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
    fake_particles.append(Particle(0, HEIGHT, radius=0, mass=math.inf, v=0, o=0, is_fake=True))
    fake_particles.append(Particle(WIDTH, HEIGHT, radius=0, mass=math.inf, v=0, o=0, is_fake=True))

    # Create particles
    for particle_count in range(arguments.n):
        new_particle = Particle.get_random_particle(max_height=HEIGHT, max_width=WIDTH / 2 - PARTICLE_RADIUS,
                                                    radius=PARTICLE_RADIUS, speed=PARTICLE_SPEED, mass=PARTICLE_MASS)

        done = False
        while not done:
            overlap = False
            # Make sure the new particle doesn't overlap with any other existing particle
            for existing_particle in particles:
                if new_particle.distance_to(existing_particle) < 0:
                    overlap = True
                    new_particle = Particle.get_random_particle(max_height=HEIGHT,
                                                                max_width=WIDTH / 2 - PARTICLE_RADIUS,
                                                                radius=PARTICLE_RADIUS, speed=PARTICLE_SPEED,
                                                                mass=PARTICLE_MASS)
                    break

            done = not overlap

        particles.append(new_particle)
    return particles, fake_particles

def get_compartment(particle):
    """Return which compartment the specified particle is in. 0 for left, 1 for exact middle, 2 for right."""
    if particle.x == WIDTH / 2:
        return 1

    return 0 if particle.x < WIDTH / 2 else 2


def time_to_border_wall_collision(particle):
    """Calculate time for the given particle to collide against any border wall. Return infinity if particle will not
    collide with a wall (e.g. if Vx = Vy = 0)."""

    # Calculate minimum collision time in x axis
    if particle.velocity.x > 0:
        collision_time_x = (WIDTH - particle.radius - particle.position.x) / particle.velocity.x
    elif particle.velocity.x < 0:
        collision_time_x = (0 + particle.radius - particle.position.x) / particle.velocity.x
    else:
        collision_time_x = math.inf

    # Calculate minimum collision time in y axis
    if particle.velocity.y > 0:
        collision_time_y = (HEIGHT - particle.radius - particle.position.y) / particle.velocity.y
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
        time = (WIDTH / 2 - particle.radius - particle.position.x) / particle.velocity.x
    elif compartment == 2:
        if particle.velocity.x >= 0:
            return math.inf
        time = (WIDTH / 2 + particle.radius - particle.position.x) / particle.velocity.x
    else:
        return math.inf  # Should only happen when inside the aperture

    new_y = particle.position.y + particle.velocity.y * time
    if (HEIGHT / 2) - (APERTURE_WIDTH / 2) + particle.radius <= new_y <= (HEIGHT / 2) + (
                APERTURE_WIDTH / 2) - particle.radius:
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

    min_collision_times = dict()
    for me in particles:
        # Get the time until this particle first collides against a wall or against another particle. Always need to
        # compare with all other particles because it is not necessarily true that
        # time_to_collision(x, y) == time_to_collision(y, x)
        collision_time, target = min_collision_time(me, particles)
        min_collision_times[me.id] = (me, collision_time, target)

    return min_collision_times


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

        global aperture_bottom_particle
        global aperture_top_particle

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

def update_collision_times(colliding_particles, particles, collision_times):
    # Update next collision of collided particle(s), and any other particles they may now collide with

    for particle in colliding_particles:
        if particle is not None:
            # Calculate new colliding times for particle
            next_collision_time, next_target = min_collision_time(particle, particles)
            collision_times[particle.id] = (particle, next_collision_time, next_target)

            # If next collision is with another particle, and if it will now happen sooner than when that other particle
            # was going to collide before, also update that particle's collision time
            if next_target is not None and next_collision_time < collision_times[next_target.id][1]:
                collision_times[next_target.id] = (next_target, next_collision_time, particle)

            # Recalculate next collision for particles that were supposed to collide with this particle
            for other_particle in particles:
                if other_particle == particle:
                    continue
                if collision_times[other_particle.id][2] == particle:
                    other_new_collision_time, other_new_target = min_collision_time(other_particle, particles)
                    collision_times[other_particle.id] = (other_particle, other_new_collision_time, other_new_target)

    return collision_times

def next_collision(collision_times):
    """Get the minimum collision time of all times in the specified data, where data has the form of what is returned
    by #min_collision_times. Return (particle, min_time, target)"""

    result = None
    min_time = math.inf

    for particle_id, (particle, time, target) in collision_times.items():
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
        if particle.y > HEIGHT:
            raise ValueError(
                'The position of the particle cannot be outside the box, the y position must be smaller than the height')
        if particle.x > WIDTH:
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
    if (WIDTH / 2) - particle.radius <= particle.x <= (WIDTH / 2) + particle.radius:
        particle.velocity.x *= -1
        return

    # Border walls
    wall_speed = 0
    if particle.y >= HEIGHT - PARTICLE_RADIUS or particle.y <= 0 + PARTICLE_RADIUS:
        particle.velocity.y *= -1
        wall_speed += math.fabs(particle.velocity.y)
    if particle.x >= WIDTH - PARTICLE_RADIUS or particle.x <= 0 + PARTICLE_RADIUS:
        particle.velocity.x *= -1
        wall_speed += math.fabs(particle.velocity.x)

    # Update pressure each time a particle collisions with a wall
    global impulse, temperature
    pv_file = open("pv_output.txt", "a")

    # Impulse equation from https://www.britannica.com/science/gas-state-of-matter/Kinetic-theory-of-gases
    if t > 0:
        impulse += 2 * particle.mass * wall_speed

    temperature = calculate_temperature(particles)

    if t != 0:
        # Pressure = impulse / time / surface
        pressure = impulse / t / (2 * WIDTH + 2 * HEIGHT + HEIGHT - APERTURE_WIDTH)
        pv_file.write("%g\t%g\n" % (pressure, temperature))
    # print("pressure: %g\t, temperature: %g\n" %(pressure,temperature))

    pv_file.close()


def particle_collision(particle1, particle2):
    # Filmina 20 de teórica 3
    delta_r = particle2.position - particle1.position
    delta_v = particle2.velocity - particle1.velocity
    o = particle1.radius + particle2.radius

    #Check if one of the colliding "particles" is a border "particle
    if particle1.mass == math.inf:
        j = 2*particle2.mass * delta_v.dot(delta_r) / o
    elif particle2.mass == math.inf:
        j = 2*particle1.mass * delta_v.dot(delta_r) / o
    else:
        j = 2 * particle1.mass * particle2.mass * delta_v.dot(delta_r) / (o * (particle1.mass + particle2.mass))

    j_x = j * delta_r.x / o
    j_y = j * delta_r.y / o

    particle1.velocity.x += j_x / particle1.mass
    particle1.velocity.y += j_y / particle1.mass

    particle2.velocity.x -= j_x / particle2.mass
    particle2.velocity.y -= j_y / particle2.mass

def recalculate_fp(particles):
# Calculate the particle ratio on each side
    left = 0
    right = 0
    for particle in particles:
        if particle.position.x <= WIDTH / 2:
            left += 1
        else:
            right += 1
    fp_left = left / arguments.n
    fp_right = right / arguments.n
    return fp_left, fp_right

def write_positions(t, fp_left, particles, fake_particles, first_frame, colliding_particle, target):
    # Render frame
    if arguments.verbose:
        print("Rendering frame, t=%g, fp=%g" % (t, fp_left))

    # Color the collided particle(s) red and blue, others in white
    colors = [(255, 255, 255)] * arguments.n
    for j in range(len(particles)):
        if particles[j] == colliding_particle:
            colors[j] = (255, 0, 0)
        elif target is not None and particles[j] == target:
            colors[j] = (0, 0, 255)

    # Color the fake middle wall particles green
    colors += [(0, 255, 0)] * len(fake_particles)

    FileWriter.export_positions_ovito(particles + fake_particles, t=t, colors=colors, output=arguments.output,
                                      mode='w' if first_frame else 'a')


def calculate_temperature(particles):
    dimension = HEIGHT * WIDTH
    # dk / N sum mv**2

    accum = 0

    for particle in particles:
        accum += particle.mass * particle.velocity.magnitude() ** 2
    temperature = (accum / arguments.n) / (2*K)

    temp_path = "temp" + str(PARTICLE_SPEED) + ".txt"
    temperatures = open(temp_path, "a")
    temperatures.write("%g\t%g\n" %(t, temperature))
    return temperature

####################################################################

# Time variables
t = 0
delta_t = 0
first_frame = True

# Particle ratio on each side of the box
fp_left = 1
fp_right = 0

# Generate particles
particles, fake_particles = generate_particles()

#TODO: ver de meter bien tema de presion
# pv_file = open("pv_output", "w")
# pv_file.write("%s\t%s\n" % ("pressure", "temperature"))
# pv_file.close()

# Calculate initial collision times
collision_times = all_min_collision_times(particles)

pv_output = open("pv_output.txt", "w")
pv_output.write("presion\ttemperatura\n")
pv_output.close()

temp_path = "temp" + str(PARTICLE_SPEED) + ".txt"
temperatures = open(temp_path, "w")
temperatures.write("time\ttemperature\n")
temperatures.close()

# Algorithm
while fp_left > arguments.cutoff:
    if arguments.verbose:
        print("Processing t=%g" % t)

    colliding_particle, min_time, target = next_collision(collision_times)

    # Subtract min_time from all collision times; colliding particle(s) will have their collision time set to 0
    for particle_id, (particle, time, target2) in collision_times.items():
        collision_times[particle_id] = (particle, time - min_time, target2)

    evolve_particles(particles, min_time, colliding_particle, target)

    collision_times = update_collision_times(colliding_particles=[colliding_particle, target], particles=particles,
                                              collision_times=collision_times)

    t += min_time
    delta_t += min_time
    fp_left, fp_right = recalculate_fp(particles)

    if delta_t >= arguments.delta:
        write_positions(t=t, fp_left=fp_left, particles=particles, fake_particles=fake_particles,
                        first_frame=first_frame, colliding_particle=colliding_particle, target=target)
        first_frame = False
        delta_t = 0


print("#: %g\t%g" %(arguments.n, t))

if arguments.verbose:
    print("Cutoff of %g reached, stopping." % arguments.cutoff)

print("Done")
