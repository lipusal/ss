import pprint

from ss.cim.cell_index_method import CellIndexMethod
from ss.util.file_writer import FileWriter
from ss.util.file_reader import FileReader
from os import path

cwd = path.dirname(__file__)
r = 6
imported_data = FileReader.import_particles(path.join(cwd, '..', '..', 'ex', '01', 'Dynamic100.txt'), path.join(cwd, '..', '..', 'ex', '01', 'Static100.txt'))
particles = imported_data['particles']

data = CellIndexMethod(*particles, interaction_radius=r)

for i in range(len(particles)):
    print('#%i: %s' % (i+1, particles[i]))

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
FileWriter.export_positions_matlab(data, 75, path.join(cwd, 'dynamic.txt'))
