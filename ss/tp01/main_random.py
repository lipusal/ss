import random
import argparse
from ss.cim.cell_index_method import CellIndexMethod
from ss.cim.particle import Particle
from ss.util.file_writer import FileWriter

parser = argparse.ArgumentParser(description="Cell Index Method program, runs method on a random set of particles")
parser.add_argument("amount", help="Amount of particles", default=100, type=int)
parser.add_argument("boardSize", help="Size of each side of the board", default=250, type=int)
parser.add_argument("radius", help="Interaction radius for all particles.", default=10.0, type=float)
parser.add_argument("--output", "-o", help="Path of output file. Defaults to './output.txt'", default="./output.txt")
parser.add_argument("--periodic", "-p", help="Make the board periodic (particles that go \"out of board\" come in from"
                                             "the other side", action="store_true", default=False)
parser.add_argument("--verbose", "-v", help="Print verbose information while running", action="store_true", default=False)
parser.add_argument("--time", "-t", help="Print elapsed program time", action="store_true", default=False)
args = parser.parse_args()

if args.time:
    import ss.util.timer

l = args.boardSize
r = args.radius

particles = []
print("Randomly generated particles:")
for i in range(args.amount):
    particles.append(Particle(random.random() * l, random.random() * l))
    print(particles[-1])
print()

data = CellIndexMethod(*particles,interaction_radius=r, is_periodic=args.periodic)

print('Writing MATLAB output')
FileWriter.export_positions_matlab(data, 0, args.output)