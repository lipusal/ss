import math
import random

from ss.cim.cell_index_method import CellIndexMethod
from ss.cim.particle import Particle
from ss.util.file_writer import FileWriter

import ss.util.args as args

# Custom arguments
args.parser.description = "Self-propulsed particles program. Simulates particles with a (random) given velocity that" \
                          "changes over time, and whose change is influenced by other particles within a radius"
args.parser.add_argument("radius", help="Interaction radius for all particles.", type=float, default=1.0)
args.parser.add_argument("eta", help="Noise that will be added when calculating the variation in angles of each "
                                     "particle", type=float)
args.parser.add_argument("-n", help="Amount of particles", type=int, default=100)
args.parser.add_argument("--iterations", "-i", help="Amount of iterations", type=int, default=100)
arguments = args.parse_args()

if arguments.time:
    import ss.util.timer

particle_velocity = 0.3
side_length = arguments.l if 'l' in arguments and arguments.l is not None else 100
particles = list()
for particle_count in range(arguments.n):
    x = random.uniform(0.0, side_length)
    y = random.uniform(0.0, side_length)
    o = random.uniform(0.0, 2 * math.pi)
    particles.append(Particle(x, y, 0.0, particle_velocity, o))

delta_t = 1


# TODO TEST

def avg_angle(neighbors):
    sin_accum = 0
    cos_accum = 0
    length = 0
    for tuple in neighbors:
        length += 1
        angle = tuple[0].vel_angle()
        sin_accum += math.sin(angle)
        cos_accum += math.cos(angle)
    return math.atan2(sin_accum / length, cos_accum / length)


for i in range(arguments.iterations):
    print("Processing frame #%i" % (i + 1))
    data = CellIndexMethod(particles, arguments)

    for particle in particles:
        # Move particle
        new_position = particle.position + (particle.velocity * delta_t)
        # Use modulo because board is periodic
        particle.move_to(new_position.x % data.l, new_position.y % data.l)

        # Change direction using neighbors
        noise = random.uniform(-arguments.eta / 2, arguments.eta / 2)
        # Calculate new direction using neighbors and self
        newVelAngle = noise + avg_angle(data.neighbors[particle.id] + [(particle, 0)])
        particle.velocity = (particle_velocity, newVelAngle)
        if arguments.verbose:
            print("Velocity of particle #%i: %s" % (particle.id, particle.velocity))

    # Truncate file for first frame, append for following frames
    FileWriter.export_positions_ovito(particles, i, 'output.txt', 'w' if i == 0 else 'a')

if arguments.verbose:
    print("Output written to %s", arguments.output)

print("Done")
