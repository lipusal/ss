import random
import pprint

from ss.cim.particle import Particle
from ss.cim.cell_index_method import CellIndexMethod
from ss.util.file_writer import FileWriter

# max = 25
# particles = []
# for i in range(100):
#     particles.append(Particle(random.random() * max, random.random() * max))
#     print(particles[-1])

particles = [Particle(8.4615324e+00, 4.5584588e+01, 0.37), Particle(3.8078434e+00, 3.0965299e+01, 0.37),
             Particle(6.2268716e+01, 2.1816192e+01, 0.37), Particle(9.2868183e+01, 1.1373036e+01, 0.37),
             Particle(3.2684529e+01, 1.2884209e+01, 0.37), Particle(7.4301847e+01, 9.3819547e+01, 0.37),
             Particle(2.9232575e+01, 4.8452965e+01, 0.37), Particle(1.2821888e+01, 7.4052807e+01, 0.37),
             Particle(5.1369479e+01, 3.0234140e+01, 0.37), Particle(3.9609457e+01, 7.1203633e-01, 0.37),
             Particle(9.7333044e+01, 6.0882952e+01, 0.37), Particle(2.9615546e+01, 3.5014446e+01, 0.37),
             Particle(5.9113179e+01, 6.4031213e+01, 0.37), Particle(5.7063444e+01, 8.3740499e+01, 0.37),
             Particle(6.0938477e+01, 9.5685537e+00, 0.37), Particle(5.6002977e+01, 5.7974486e+01, 0.37),
             Particle(2.8290847e+01, 5.7433808e+01, 0.37), Particle(1.5662992e+01, 5.1465160e+01, 0.37),
             Particle(7.2909000e+01, 4.4694359e+01, 0.37), Particle(4.3400845e+00, 9.5893685e+01, 0.37),
             Particle(7.9426082e+01, 1.7785581e+01, 0.37), Particle(4.0784530e+01, 5.5090897e+01, 0.37),
             Particle(8.2600308e+01, 6.1886282e+01, 0.37), Particle(9.6245043e+01, 2.9580718e+00, 0.37),
             Particle(4.2352182e+01, 6.3373342e+01, 0.37), Particle(5.7950909e+00, 8.3056942e+01, 0.37),
             Particle(7.8198211e+01, 3.8817509e+01, 0.37), Particle(6.2762644e+01, 4.2909610e+01, 0.37),
             Particle(5.0794349e+01, 7.6327458e+00, 0.37), Particle(5.6669285e+01, 5.7283245e+01, 0.37),
             Particle(3.1103601e+01, 8.6327959e+01, 0.37), Particle(7.4054122e+01, 2.0138322e+01, 0.37),
             Particle(3.4411155e+01, 9.0309962e+00, 0.37), Particle(8.7563064e+01, 1.8416426e+01, 0.37),
             Particle(3.3543689e+01, 6.6390813e+01, 0.37), Particle(7.9279206e+01, 7.2444470e+01, 0.37),
             Particle(8.0104335e+01, 6.2326363e+01, 0.37), Particle(5.6202381e+00, 4.6200624e+01, 0.37),
             Particle(4.0506774e+01, 3.0615037e+01, 0.37), Particle(9.6014204e+01, 6.3450203e+01, 0.37),
             Particle(4.1568058e+01, 5.5352382e+01, 0.37), Particle(3.3112866e+01, 6.5821450e+01, 0.37),
             Particle(6.3003075e+01, 1.1906457e+01, 0.37), Particle(8.5399080e+01, 6.6642936e+01, 0.37),
             Particle(7.8492857e+01, 6.7239006e+01, 0.37), Particle(5.3805575e+01, 9.2152484e+01, 0.37),
             Particle(7.3926331e+01, 8.2056074e+01, 0.37), Particle(7.3281649e+01, 1.7296841e+01, 0.37),
             Particle(4.4529957e+01, 9.4065286e+01, 0.37), Particle(8.4293571e+01, 1.9536356e+01, 0.37),
             Particle(4.9477459e+01, 2.0908162e+01, 0.37), Particle(9.3955648e+01, 8.3583423e-01, 0.37),
             Particle(7.9173533e+01, 2.9451373e+01, 0.37), Particle(1.3993743e+01, 2.6932367e+01, 0.37),
             Particle(2.4128811e+01, 5.7859825e+01, 0.37), Particle(1.3361650e+01, 3.9028573e+01, 0.37),
             Particle(5.3257659e+01, 1.7794031e+01, 0.37), Particle(6.3139088e+00, 3.8711551e+01, 0.37),
             Particle(4.7031980e+01, 1.4617047e+01, 0.37), Particle(9.7837275e+01, 8.2486234e+01, 0.37),
             Particle(6.7557686e+01, 1.4428802e+01, 0.37), Particle(8.6678021e+01, 6.7199440e+01, 0.37),
             Particle(4.9626102e+01, 7.4148754e+01, 0.37), Particle(2.9624386e+01, 1.4289900e+00, 0.37),
             Particle(1.9087035e+01, 1.3872997e+01, 0.37), Particle(9.5263535e+01, 3.0084938e+00, 0.37),
             Particle(7.5366378e+01, 8.0049451e+01, 0.37), Particle(9.4179766e+01, 4.6250048e+00, 0.37),
             Particle(6.6912592e+01, 6.5784952e+01, 0.37), Particle(1.9093907e+01, 4.4895102e+01, 0.37),
             Particle(2.9202596e+01, 7.9467563e+01, 0.37), Particle(6.4891878e+00, 3.5302336e+01, 0.37),
             Particle(5.2655618e+00, 2.4857404e+00, 0.37), Particle(2.8567561e+01, 2.1253928e+01, 0.37),
             Particle(1.7409292e+01, 7.0311257e+01, 0.37), Particle(6.7446059e+01, 5.4073332e+01, 0.37),
             Particle(8.9880616e+01, 8.6188536e+01, 0.37), Particle(3.5368381e+01, 7.3040200e+01, 0.37),
             Particle(1.0848878e+01, 1.0108268e+01, 0.37), Particle(7.9051888e+01, 9.6319686e+01, 0.37),
             Particle(4.6880679e+01, 7.3011817e+01, 0.37), Particle(6.7876207e+01, 1.3222531e+00, 0.37),
             Particle(6.8084057e+01, 6.7081529e+01, 0.37), Particle(4.2282043e+01, 4.7701231e+01, 0.37),
             Particle(6.5093748e+01, 3.2885440e+00, 0.37), Particle(6.2690019e+01, 1.0883607e+01, 0.37),
             Particle(5.2247811e+01, 6.8449433e+00, 0.37), Particle(1.9518318e+01, 6.0015780e+01, 0.37),
             Particle(5.1147192e+01, 2.2487453e+01, 0.37), Particle(7.4086344e+01, 1.3773937e+01, 0.37),
             Particle(4.2112272e+01, 5.2166878e+01, 0.37), Particle(7.3535253e+01, 9.2196582e+01, 0.37),
             Particle(6.8397999e+01, 6.0866776e+01, 0.37), Particle(9.5098523e+01, 6.8271351e+01, 0.37),
             Particle(3.1336904e+01, 2.2778027e+01, 0.37), Particle(3.4752904e+01, 2.0001236e+01, 0.37),
             Particle(3.9520498e+01, 3.4677105e+00, 0.37), Particle(3.1180257e+00, 6.5636774e+01, 0.37),
             Particle(6.3135785e+01, 4.9893507e+01, 0.37), Particle(5.6410770e+01, 4.7727423e+01, 0.37)]
r = 6
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
FileWriter.export_positions_matlab(data, 75)
