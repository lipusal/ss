import matplotlib.pyplot as plt
import numpy as np

import ss.util.args as arg_base
from ss.cim.particle import Particle
import ss.tp04.oscillator.constants as constants
from ss.tp04.solutions import real, euler_modified, beeman, verlet

# TODO: Update description
arg_base.parser.description = "Gas Diffusion simulation Program. Simulates how a number of given gas particles diffuse " \
                          "from one compartment to another through a slit"

args = arg_base.parse_args()

# ----------------------------------------------------------------------------------------------------------------------
#       MAIN
# ----------------------------------------------------------------------------------------------------------------------

real_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0, o=0.0)
euler_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0, o=0.0)
beeman_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0, o=0.0)
verlet_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0, o=0.0)
times, positions_real, positions_euler, positions_beeman, positions_verlet = [], [], [], [], []
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
    beeman_x = beeman.x(particle=beeman_particle, delta_t=delta_t)
    positions_beeman.append(beeman_x.x)
    beeman_particle.position = beeman_x
    # TODO remover euler use beeman only for testing
    beeman_particle.velocity = euler_modified.v(particle=beeman_particle, delta_t=delta_t)

    # Calculate verlets particle new position
    verlet_x = verlet.x(particle=verlet_particle, delta_t=delta_t)
    positions_verlet.append(verlet_x.x)
    verlet_particle.position = verlet_x
    verlet_particle.velocity = verlet.v(particle=verlet_particle, delta_t=delta_t)

    # print("x(%g) = %g" % (times[-1], positions_real[-1]))

plt.plot(times, positions_real)
# plt.plot(times, positions_euler)
# plt.plot(times, positions_beeman)
plt.plot(times, positions_verlet)
plt.show()
