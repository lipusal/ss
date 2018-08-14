import random
from ss.cim.cell_index_method import CellIndexMethod
from ss.cim.particle import Particle
from ss.util.file_writer import FileWriter
import ss.util.args as arg_utils

# Custom arguments
arg_utils.parser.description = "Cell Index Method program that generates random particles"
arg_utils.parser.add_argument("amount", help="Amount of particles to generate", default=100, type=int)
arg_utils.parser.add_argument("radius", help="Interaction radius for all particles.", default=10.0, type=float)
args = arg_utils.to_dict_no_none()

if 'width' not in args:
    raise Exception("width argument is required for this program")

if 'time' in args:
    import ss.util.timer

l = args['width']
r = args['radius']

particles = []
print("Randomly generated particles:")
for i in range(args['amount']):
    particles.append(Particle(random.random() * l, random.random() * l))
    print(particles[-1])
print()

# FIXME fix method call, use same args from args.py
data = CellIndexMethod(particles, **args)

print('Writing MATLAB output to %s' % args['output'])
FileWriter.export_positions_matlab(data, 0, args['output'])
