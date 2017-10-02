import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

import ss.util.args as arg_base
from ss.cim.particle import Particle
import ss.tp04.oscillator.constants as constants
from ss.tp04.oscillator.constants import *
from ss.tp04.solutions import real, euler_modified, beeman, verlet, gear_predictor

# TODO: Update description
arg_base.parser.description = "Dampened oscillator simulation program. Uses different integration methods to compare " \
                              "their accuracy by measuring their distance to the analytical (ie. real) solution."
arg_base.parser.add_argument("--integration_method", "-im",
                             help="Choose integration method: euler, beeman, verlet, gear or all", type=str, nargs='*',
                             default="all")

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
euler_particle.previous_acceleration = initial_previous_acceleration(euler_particle, delta_t, f(euler_particle.position,
                                                                                                euler_particle.velocity))
# Create particle that will be used to test beeman
beeman_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0, o=0.0)
beeman_particle.previous_acceleration = initial_previous_acceleration(beeman_particle, delta_t,
                                                                      f(beeman_particle.position,
                                                                        beeman_particle.velocity))
# Create particle that will be used to test verlet
verlet_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0, o=0.0)
# Create particle that will be used to test gear predictor
gear_predictor_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0,
                                   o=0.0)
times, positions_real, positions_euler, positions_beeman, positions_verlet, positions_gear_predictor = [], [], [], [], [], []

euler_error, beeman_error, verlet_error, gear_error = 0, 0, 0, 0

iteration = 0

for t in np.arange(0, 4, delta_t):
    iteration += 1
    times.append(t)
    positions_real.append(real.x(t))

    # Calculate euler particle new position
    if "euler" in args.integration_method or "all" in args.integration_method:
        euler_force = f(euler_particle.position, euler_particle.velocity)
        euler_x = euler_modified.x(particle=euler_particle, delta_t=delta_t, force=euler_force)
        positions_euler.append(euler_x.x)
        euler_particle.position = euler_x
        euler_particle.velocity = euler_modified.v(particle=euler_particle, delta_t=delta_t, force=euler_force)
        euler_error += (euler_x[0] - real.x(t)) ** 2

    # Calculate beeman particles new position
    if "beeman" in args.integration_method or "all" in args.integration_method:
        beeman_force = f(beeman_particle.position, beeman_particle.velocity)
        beeman_x = beeman.r(particle=beeman_particle, delta_t=delta_t, force=beeman_force)
        positions_beeman.append(beeman_x.x)
        beeman_particle.position = beeman_x
        beeman_particle.velocity = beeman.v(particle=beeman_particle, delta_t=delta_t, force=beeman_force, f=f)
        beeman_error += (beeman_x[0] - real.x(t)) ** 2

    # Calculate verlet particle new position
    if "verlet" in args.integration_method or "all" in args.integration_method:
        verlet_force = f(verlet_particle.position, verlet_particle.velocity)
        verlet_x = verlet.r(particle=verlet_particle, delta_t=delta_t, force=verlet_force)
        positions_verlet.append(verlet_x.x)
        verlet_particle.position = verlet_x
        verlet_particle.velocity = verlet.v(particle=verlet_particle, delta_t=delta_t, force=verlet_force)
        verlet_error += (verlet_x[0] - real.x(t)) ** 2

    # Calculate gear predictor particle new position
    if "gear" in args.integration_method or "all" in args.integration_method:
        gear_predictor_derivatives = gear_predictor.run(particle=gear_predictor_particle, delta_t=delta_t)
        positions_gear_predictor.append(gear_predictor_derivatives[0].x)
        gear_predictor_particle.position = gear_predictor_derivatives[0]
        gear_predictor_particle.velocity = gear_predictor_derivatives[1]
        gear_error += (gear_predictor_derivatives[0].x - real.x(t)) ** 2

plt.plot(times, positions_real, 'r:', label="Analítico")

# Check parameters to see what to graph
if "euler" in args.integration_method or "all" in args.integration_method:
    plt.plot(times, positions_euler, 'c:', label="Euler")

if "beeman" in args.integration_method or "all" in args.integration_method:
    plt.plot(times, positions_beeman, 'm:', label="Beeman")

if "verlet" in args.integration_method or "all" in args.integration_method:
    plt.plot(times, positions_verlet, 'b:', label="Verlet")

if "gear" in args.integration_method or "all" in args.integration_method:
    plt.plot(times, positions_gear_predictor, 'g:', label="Gear predictor 5")

plt.legend()

print("Mean Quadratic Errors")
print("Euler: %f" % (euler_error / iteration))
print("Beeman: %f" % (beeman_error / iteration))
print("Verlet: %f" % (verlet_error / iteration))
print("Gear Predictor: %f" % (gear_error / iteration))

plt.ylabel('Amplitud')
plt.xlabel('Tiempo')
plt.title('Oscilador Amortiguado')
plt.show()
