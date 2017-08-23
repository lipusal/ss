import pprint
from ss.tp01 import args
from os import path

from ss.cim.cell_index_method import CellIndexMethod
from ss.util.file_reader import FileReader
from ss.util.file_writer import FileWriter

# Parse args
args = args.parse_args()

if args.time:
    import ss.util.timer

if args.verbose:
    print("Received arguments: ", end='')
    pprint.pprint(args)

# Normalize paths so they work in any machine
args.dynamic = path.normpath(args.dynamic)
args.output = path.normpath(args.output)
if not args.static is None:
    args.static = path.normpath(args.static)

imported_data = FileReader.import_particles(args.dynamic, args.static) if args.static else FileReader.import_particles(args.dynamic)
particles = imported_data['particles']

data = CellIndexMethod(*particles, interaction_radius=args.radius, is_periodic=args.periodic)

if args.verbose:
    for i in range(len(particles)):
        print('#%i: %s' % (i + 1, particles[i]))

    print('# of particles per cell:')
    print(data)

    print('Writing MATLAB output')

FileWriter.export_positions_matlab(data, 0, args.output)    # Paint the first particle and all its neighbors
# FileWriter.export_positions_matlab(data, 23, args.output)
# FileWriter.export_positions_ovito(data.particles, output=args.output + ".ovito.txt")
print("Done")
