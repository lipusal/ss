import random
import pprint

from ss.cim.particle import Particle
from ss.cim.cell_index_method import CellIndexMethod

l = 25
m = 5
r = 3

particles = []
for i in range(100):
    particles.append(Particle(random.random() * l, random.random() * l))
    print(particles[-1])

la = CellIndexMethod(*particles, interaction_radius=r)

print('# of particles per cell:')

for row in range(m):
    print('|', end='')
    for col in range(m):
        print("%i|" % len(la.board[row][col].particles), end='')
    print()

print('Distances:')
pprint.pprint(la.distances)