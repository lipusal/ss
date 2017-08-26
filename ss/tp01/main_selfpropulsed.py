from ss.cim.cell_index_method import CellIndexMethod
from ss.cim.particle import Particle
from ss.util.file_writer import FileWriter

import argparse
import math
import random

# Parse args
parser = argparse.ArgumentParser(description="------")# TODO
parser.add_argument("radius", help="Interaction radius for all particles.", type=float, default=1.0)
parser.add_argument("eta", help="Noise that will be added when calculating the variation in angles of each particle", type=float)
parser.add_argument("-l", help="Board side length. Integer. If not provided, will calculate a minimum bounding box "
                               "containing all particles", type=float, default=100.0)
parser.add_argument("-n", help="Amount of particles", type=int, default=100)
parser.add_argument("--iterations", "-i", help="Amount of iterations", type=int, default=100)
parser.add_argument("--time", "-t", help="Print elapsed program time", action="store_true", default=False)
args = parser.parse_args()

if args.time:
    import ss.util.timer

#TODO randomize
# imported_data = FileReader.import_particles("../../ex/01/Dynamic100.txt", "../../ex/01/Static100.txt")
# particles = imported_data['particles']

particle_velocity = 0.3
particles = list()
for particle_count in range (args.iterations):
    x = random.uniform(0.0, args.l)
    y = random.uniform(0.0, args.l)
    o = random.uniform(0.0, 2*math.pi)
    particles.append(Particle(x, y, 0.0, particle_velocity, o))

delta_t = 1

# TODO TEST

print(particles)

def avg_angle(neighbors):
    sin_accum = 0
    cos_accum = 0
    len = 0
    for n in neighbors:
        len+=1
        sin_accum += math.sin(n[0].vel_angle())
        cos_accum += math.cos(n[0].vel_angle())
    return (sin_accum/len)/(cos_accum/len)

for i in range (1,args.iterations):
    data = CellIndexMethod(particles, args)
    for n in data.neighbors:
        for particleTuple in data.neighbors[n]:
            particle = particleTuple [0]

            #move position
            newPositionX = particle.x + particle.velocity[0]*delta_t
            newPositionY = particle.y + particle.velocity[1]*delta_t
            particle.move_to(newPositionX, newPositionY)

            #change direction
            noise = random.uniform((-args.eta / 2), args.eta/2)
            newVelAngle = noise + avg_angle(data.neighbors[n])
            particle.velocity = (particle_velocity, newVelAngle)
            print(particle.velocity)

print("Done")
