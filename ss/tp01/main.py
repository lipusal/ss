import argparse
import pprint
from os import path

from ss.cim.cell_index_method import CellIndexMethod
from ss.util.file_reader import FileReader
from ss.util.file_writer import FileWriter

# Prepare argument parser
parser = argparse.ArgumentParser(description="Cell Index Method program, runs method on a given set of particles")
parser.add_argument("dynamic", help="Path of dynamic file from which to read time and particle positions")
parser.add_argument("static", nargs="?",
                    help="(Optional) Path of static file from which to read particle radii and properties",
                    default=None)
parser.add_argument("radius", help="Interaction radius for all particles.", type=float)
parser.add_argument("--output", "-o", help="Path of output file. Defaults to './output.txt'", default="./output.txt")
parser.add_argument("--periodic", "-p", help="Make the board periodic (particles that go \"out of board\" come in from"
                                             "the other side", action="store_true", default=False)
parser.add_argument("--verbose", "-v", help="Print verbose information while running", action="store_true", default=False)
parser.add_argument("--time", "-t", help="Print elapsed program time", action="store_true", default=False)
args = parser.parse_args()

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
        # TODO: Move this to CellIndexMethod#__str__
        for row in reversed(range(data.cells_per_row)):
            print('|', end='')
            for col in range(data.cells_per_row):
                print("%i|" % len(data.board[row][col].particles), end='')
            print()

        print('Distances:')
        pprint.pprint(data.distances)

        print('Writing MATLAB output')
FileWriter.export_positions_matlab(data, 0, args.output)
# FileWriter.export_positions_matlab(data, 23, args.output)

print("Done")
