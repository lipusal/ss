import random
import pprint

from ss.cim.particle import Particle
from ss.cim.cell_index_method import CellIndexMethod
from ss.util.file_writer import FileWriter

max = 25
r = 3

particles = []
for i in range(100):
    particles.append(Particle(random.random() * max, random.random() * max))
    print(particles[-1])

data = CellIndexMethod(*particles, interaction_radius=r)

print('# of particles per cell:')
# TODO: Move this to CellIndexMethod#__str__
for row in reversed(range(data.cells_per_row)):
    print('|', end='')
    for col in range(data.cells_per_row):
        print("%i|" % len(data.board[row][col].particles), end='')
    print()

print('Distances:')
pprint.pprint(data.distances)

print('Writing MATLAB output')
FileWriter.export_positions_matlab(data)