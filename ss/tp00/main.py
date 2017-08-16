import random

from ss.util import cell_index_method
import ss.util.particle

l = 25
m = 5
r = 3

particles = []
for i in range(100):
    particles.append(ss.util.particle.Particle(random.random() * l, random.random() * l))
    print(particles[-1])

la = cell_index_method.CellIndexMethod(l, m, r, particles)
cells = la.particlesInCells()

print()

for row in range(m):
    print('|', end='')
    for col in range(m):
        print("%i|" % len(cells[row][col]), end='')
    print()
