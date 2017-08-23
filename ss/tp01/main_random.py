import random

from ss.cim.cell_index_method import CellIndexMethod
from ss.cim.particle import Particle
from ss.util.file_writer import FileWriter

l = 25
m = 5
r = 10

particles = []
print("Randomly generated particles:")
for i in range(100):
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