import matplotlib.pyplot as plt
import numpy as np

import ss.util.args as arg_base
from ss.cim.particle import Particle
import ss.tp04.oscillator.constants as constants
from ss.tp04.oscillator.constants import *
from ss.tp04.solutions import real, euler_modified, beeman, verlet, gear_predictor

# TODO: Update description
arg_base.parser.description = "Dampened oscillator simulation program. Uses different integration methods to compare " \
                              "their accuracy by measuring their distance to the analytical (ie. real) solution."
args = arg_base.parse_args()

# ----------------------------------------------------------------------------------------------------------------------
#       MAIN
# ----------------------------------------------------------------------------------------------------------------------



# noinspection PyPep8Naming
def f(position, velocity):
    return (-K * position) - (lamb * velocity)


real_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0, o=0.0)
euler_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0, o=0.0)
beeman_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0, o=0.0)
verlet_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0, o=0.0)
gear_predictor_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0, o=0.0)
times, positions_real, positions_euler, positions_beeman, positions_verlet, positions_gear_predictor = [], [], [], [], [], []
delta_t = 0.0001
for t in np.arange(0, 10, delta_t):

    times.append(t)
    positions_real.append(real.x(t))

    # Calculate euler particle new position
    euler_x = euler_modified.x(particle=euler_particle, delta_t=delta_t)
    positions_euler.append(euler_x.x)
    euler_particle.position = euler_x
    euler_particle.velocity = euler_modified.v(particle=euler_particle, delta_t=delta_t)

    # Calculate beeman particles new position
    beeman_x = beeman.x(particle=beeman_particle, delta_t=delta_t, f=f)
    positions_beeman.append(beeman_x.x)
    beeman_particle.position = beeman_x
    beeman_particle.velocity = beeman.v(particle=beeman_particle, delta_t=delta_t, f=f)

    # Calculate verlets particle new position
    verlet_x = verlet.x(particle=verlet_particle, delta_t=delta_t)
    positions_verlet.append(verlet_x.x)
    verlet_particle.position = verlet_x
    verlet_particle.velocity = verlet.v(particle=verlet_particle, delta_t=delta_t)

    # Calculate euler particle new position
    gear_predictor_derivatives = gear_predictor.run(particle=euler_particle, delta_t=delta_t)
    positions_gear_predictor.append(gear_predictor_derivatives[0].x)
    euler_particle.position = gear_predictor_derivatives[0]
    euler_particle.velocity = gear_predictor_derivatives[1]


    # print("x(%g) = %g" % (times[-1], positions_real[-1]))

plt.plot(times, positions_real)
# plt.plot(times, positions_euler)
plt.plot(times, positions_beeman)
# plt.plot(times, positions_verlet)
# plt.plot(times, positions_gear_predictor)
plt.show()

