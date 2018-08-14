# Add project to python path so this can be run from the command line, https://stackoverflow.com/a/23891673/2333689
import sys
import os

# NOTE: Adjust the number of ".." to get to the project's root directory (i.e. where doc, ex, and ss are, NOT inside ss
# where cim, util, etc. are)
sys.path.append(os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..")))

import math
import random
import colorsys
import euclid3
import numpy as np

from ss.cim.cell_index_method import CellIndexMethod
from ss.cim.particle import Particle
from ss.util.file_writer import FileWriter

import ss.util.args as args

# Custom arguments
# NOTE: For this script, N, L and eta will be overridden.  All other parameters are necessary.
args.parser.description = "Self-propulsed particles program. Simulates particles with a (random) given velocity that" \
                          "changes over time, and whose change is influenced by other particles within a radius"
args.parser.add_argument("radius", help="Interaction radius for all particles.", type=float, default=1.0)
args.parser.add_argument("eta", help="Noise that will be added when calculating the variation in angles of each "
                                     "particle", type=float)
args.parser.add_argument("-n", help="Amount of particles", type=int, default=100)
args.parser.add_argument("--iterations", "-i", help="Amount of iterations", type=int, default=100)
arguments = args.to_dict_no_none()

if 'time' in arguments:
    import ss.util.timer

for N,L in [(40, 3), (100, 5), (400, 10), (4000, 31), (10000, 50)]:
    for eta in np.arange(0, 5, 0.1):
        arguments['n'] = N
        arguments['l'] = L
        arguments['eta'] = eta

        # Run program
        print("-------------------------------")
        print("Running with N=%i, L=%i, eta=%g" % (N, L, eta))
        print("-------------------------------")

        particle_velocity = 0.3
        side_length = arguments.get('l', 100)
        particles = list()
        for particle_count in range(arguments['n']):
            x = random.uniform(0.0, side_length)
            y = random.uniform(0.0, side_length)
            o = random.uniform(0.0, 2 * math.pi)
            particles.append(Particle(x, y, radius=0.0, v=particle_velocity, o=o))

        delta_t = 1
        prefix = "N%i_L%i_eta%g.txt" % (N, L, eta)


        def avg_angle(neighbors):
            sin_accum = 0
            cos_accum = 0
            length = 0
            for tuple in neighbors:
                length += 1
                angle = tuple[0].vel_angle()
                sin_accum += math.sin(angle)
                cos_accum += math.cos(angle)
            return math.atan2(sin_accum / length, cos_accum / length)


        def radians_to_rgb(theta):
            """Converts an angle (in radians, (-pi, pi]) to a color using the HSV scale, and converts that to an RGB color
            which is compatible with Ovito"""

            # HSV -> RGB function requires values between 0 and 1, so map -pi < theta <= pi to 0 <= theta <= 1
            # https://stackoverflow.com/questions/345187/math-mapping-numbers#comment36962941_345204
            mapped_theta = (theta + math.pi) / (math.pi + math.pi)
            return colorsys.hsv_to_rgb(mapped_theta, 1, 1)


        # MAIN
        v_as = [[], []] # "Tuples" of the form (t, Va)
        for i in range(arguments['iterations']):
            print("Processing frame #%i" % (i + 1))
            data = CellIndexMethod(particles, **arguments)
            # Color each particle according to its direction
            colors = []
            # For calculating Va
            v_accum = euclid3.Vector2()

            for particle in particles:
                # Move particle
                new_position = particle.position + (particle.velocity * delta_t)
                # Use modulo because board is periodic
                particle.move_to(new_position.x % data.width, new_position.y % data.width)

                # Change direction using neighbors
                noise = random.uniform(-arguments['eta'] / 2, arguments['eta'] / 2)
                # Calculate new direction using neighbors and self
                newVelAngle = noise + avg_angle(data.neighbors[particle.id] + [(particle, 0)])
                particle.velocity = (particle_velocity, newVelAngle)
                if arguments['verbose']:
                    print("Velocity of particle #%i: %s" % (particle.id, particle.velocity))

                # Color particle according to its angle
                colors.append(radians_to_rgb(newVelAngle))

                v_accum += particle.velocity

            # Process Va, absolute value of average normalized velocity
            v_a = v_accum.magnitude() / (arguments['n'] * particle_velocity)
            v_as[0].append(i)
            v_as[1].append(v_a)
            # Write this run's average Va to output file
            if i == arguments['iterations'] - 1:
                file = open(("%s_va.txt" % prefix), 'w')
                file.write("%g\n" % (sum(v_as[1]) / len(v_as[1])))
                file.close()

            # Truncate file for first frame, append for following frames
            FileWriter.export_positions_ovito(particles, i, colors, ("%s_positions.txt" % prefix), 'w' if i == 0 else 'a')

        if arguments['verbose']:
            print("Output written to %s", arguments['output'])

print("Done")
