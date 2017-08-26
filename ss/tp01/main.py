import pprint
import ss.util.args as arg_utils
from os import path

from ss.cim.cell_index_method import CellIndexMethod
from ss.util.file_reader import FileReader
from ss.util.file_writer import FileWriter

# Add custom arguments
arg_utils.parser.description = "Base Cell Index Method program. Reads particles from a file, optionally reads " \
                               "particle properties from another file, and performs cell index method for 1 frame."
arg_utils.parser.add_argument("dynamic", help="Path of dynamic file from which to read time and particle positions")
arg_utils.parser.add_argument("static", nargs="?",
                         help="(Optional) Path of static file from which to read particle radii and properties",
                         default=None)
arg_utils.parser.add_argument("radius", help="Interaction radius for all particles.", type=float)
# Parse arguments
args = arg_utils.parse_args()

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

imported_data = FileReader.import_particles(args.dynamic, args.static) if args.static else FileReader.import_particles(
    args.dynamic)
particles = imported_data['particles']

data = CellIndexMethod(particles, args)

if args.verbose:
    for i in range(len(particles)):
        print('#%i: %s' % (i + 1, particles[i]))

    print('# of particles per cell:')
    print(data)

    print('Writing MATLAB output to %s' % args.output)

FileWriter.export_positions_matlab(data, 0, args.output)  # Paint the first particle and all its neighbors
# FileWriter.export_positions_matlab(data, 23, args.output)
# FileWriter.export_positions_ovito(data.particles, output=args.output + ".ovito.txt")
print("Done")
