from ss.cim.cell_index_method import CellIndexMethod
from ss.cim.particle import Particle
from ss.util.file_writer import FileWriter

import argparse
import math
import random

# Parse args
parser = argparse.ArgumentParser(description="------")  # TODO
parser.add_argument("radius", help="Interaction radius for all particles.", type=float, default=1.0)
parser.add_argument("eta", help="Noise that will be added when calculating the variation in angles of each particle",
                    type=float)
parser.add_argument("-l", help="Board side length. Integer. If not provided, will calculate a minimum bounding box "
                               "containing all particles", type=float)
parser.add_argument("-n", help="Amount of particles", type=int, default=100)
parser.add_argument("--iterations", "-i", help="Amount of iterations", type=int, default=100)
parser.add_argument("--time", "-t", help="Print elapsed program time", action="store_true", default=False)
parser.add_argument("--periodic", "-p", help="Make the board periodic (particles that go \"out of board\" come in from"
                                             "the other side", action="store_true", default=False)
parser.add_argument("-m", help="Cells per row. Integer. If not provided, will calculate an optimal value for the "
                               "particles", type=int)
parser.add_argument("--verbose", "-v", help="Print verbose information while running", action="store_true",
                    default=False)
args = parser.parse_args()

if args.time:
    import ss.util.timer

# TODO randomize
# imported_data = FileReader.import_particles("../../ex/01/Dynamic100.txt", "../../ex/01/Static100.txt")
# particles = imported_data['particles']

particle_velocity = 0.3
side_length = args.l if 'l' in args and args.l is not None else 100
particles = list()
for particle_count in range(args.iterations):
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
        neighbor = tuple[0]
        sin_accum += math.sin(neighbor.vel_angle())
        cos_accum += math.cos(neighbor.vel_angle())
    return (sin_accum / length) / (cos_accum / length)


for i in range(args.iterations):
    print("Processing frame #%i" % (i+1))
    data = CellIndexMethod(particles, args)
    for n in data.neighbors:
        for particleTuple in data.neighbors[n]:
            particle = particleTuple[0]

            # move position
            newPositionX = particle.x + particle.velocity[0] * delta_t
            newPositionY = particle.y + particle.velocity[1] * delta_t
            # Use modulo because board is periodic
            particle.move_to(newPositionX % data.l, newPositionY % data.l)

            # change direction
            noise = random.uniform((-args.eta / 2), args.eta / 2)
            newVelAngle = noise + avg_angle(data.neighbors[n])
            particle.velocity = (particle_velocity, newVelAngle)
            if args.verbose:
                print("Velocity of particle #%i: %s" % (particle.id, particle.velocity))

    # Truncate file for first frame, append for following frames
    FileWriter.export_positions_ovito(particles, i, 'output.txt', 'w' if i == 0 else 'a')

print("Done")
