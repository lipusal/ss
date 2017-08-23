import random
import argparse
from ss.cim.cell_index_method import CellIndexMethod
from ss.cim.particle import Particle
from ss.util.file_writer import FileWriter

parser = argparse.ArgumentParser(description="Cell Index Method program, runs method on a random set of particles")
parser.add_argument("amount", help="Amount of particles", default=100, type=int)
parser.add_argument("boardSize", help="Size of each side of the board", default=250, type=int)
parser.add_argument("radius", help="Interaction radius for all particles.", default=10.0, type=float)
args = parser.parse_args()

l = args.boardSize
r = args.radius

particles = []
print("Randomly generated particles:")
for i in range(args.amount):
    particles.append(Particle(random.random() * l, random.random() * l))
    print(particles[-1])
print()

data = CellIndexMethod(*particles,interaction_radius=r, is_periodic=True)

print("Amount of particles per cell")
aux = 0
for row in data.board:
    for cell in row:
        print(len(cell.particles), end='|')
        aux += len(cell.particles)
    print()

print()
print("Amount of particles:", aux, end='\n\n')
print('Writing MATLAB output')
FileWriter.export_positions_matlab(data)