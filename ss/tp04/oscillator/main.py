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

def initial_previous_acceleration(particle, delta_t, force):
    """Use Euler to simulate backwards to where it would have been"""
    # We're in initial step, use Euler to simulate backwards
    vel = euler_modified.v(particle, -delta_t, force)
    prev_acceleration = f(particle.position, vel) / particle.mass
    return prev_acceleration


# noinspection PyPep8Naming
def f(position, velocity):
    return (-K * position) - (lamb * velocity)

delta_t = 0.001

real_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0, o=0.0)
# Create particle that will be used to test euler
euler_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0, o=0.0)
euler_particle.previous_acceleration = initial_previous_acceleration(euler_particle, delta_t, f(euler_particle.position, euler_particle.velocity))
# Create particle that will be used to test beeman
beeman_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0, o=0.0)
beeman_particle.previous_acceleration = initial_previous_acceleration(beeman_particle, delta_t, f(beeman_particle.position, beeman_particle.velocity))
# Create particle that will be used to test verlet
verlet_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0, o=0.0)
# Create particle that will be used to test gear predictor
gear_predictor_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0, o=0.0)
times, positions_real, positions_euler, positions_beeman, positions_verlet, positions_gear_predictor = [], [], [], [], [], []

for t in np.arange(0, 4, delta_t):

    times.append(t)
    positions_real.append(real.x(t))

    # Calculate euler particle new position
    euler_force = f(euler_particle.position, euler_particle.velocity)
    euler_x = euler_modified.x(particle=euler_particle, delta_t=delta_t, force=euler_force)
    positions_euler.append(euler_x.x)
    euler_particle.position = euler_x
    euler_particle.velocity = euler_modified.v(particle=euler_particle, delta_t=delta_t, force=euler_force)

    # Calculate beeman particles new position
    beeman_force = f(beeman_particle.position, beeman_particle.velocity)
    beeman_x = beeman.x(particle=beeman_particle, delta_t=delta_t, force=beeman_force)
    positions_beeman.append(beeman_x.x)
    beeman_particle.position = beeman_x
    beeman_particle.velocity = beeman.v(particle=beeman_particle, delta_t=delta_t, force=beeman_force)

    # Calculate verlets particle new position
    verlet_force = f(verlet_particle.position, verlet_particle.velocity)
    verlet_x = verlet.r(particle=verlet_particle, delta_t=delta_t, force=verlet_force)
    positions_verlet.append(verlet_x.x)
    verlet_particle.position = verlet_x
    verlet_particle.velocity = verlet.v(particle=verlet_particle, delta_t=delta_t, force=verlet_force)

    # Calculate euler particle new position
    gear_predictor_derivatives = gear_predictor.run(particle=euler_particle, delta_t=delta_t)
    positions_gear_predictor.append(gear_predictor_derivatives[0].x)
    euler_particle.position = gear_predictor_derivatives[0]
    euler_particle.velocity = gear_predictor_derivatives[1]


    # print("x(%g) = %g" % (times[-1], positions_real[-1]))

plt.plot(times, positions_real, 'r--')
plt.plot(times, positions_euler, 'c--')
# plt.plot(times, positions_beeman, 'm--')
plt.plot(times, positions_verlet, 'b--')
plt.plot(times, positions_gear_predictor, 'g--')
# TODO poner bien estos titulitos
plt.ylabel('amplitud')
plt.xlabel('tiempo')
plt.title('Oscilador Armónico Simple')
plt.show()

