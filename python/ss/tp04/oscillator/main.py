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
arg_base.parser.add_argument("--integration_method", "-im",
                             help="Choose integration method: euler, beeman, verlet, gear or all", type=str, nargs='*',
                             default="all")

args = arg_base.parse_args()




def initial_previous_acceleration(particle, delta_t, force):
    """Use Euler to simulate backwards to where it would have been"""
    # We're in initial step, use Euler to simulate backwards
    vel = euler_modified.v(particle, -delta_t, force)
    prev_acceleration = f(particle.position, vel) / particle.mass
    return prev_acceleration

def generate_particles():
    real_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0,
                             o=0.0)

    # Create particle that will be used to test euler
    euler_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0,
                              o=0.0)
    euler_particle.previous_acceleration = initial_previous_acceleration(euler_particle, delta_t,
                                                                         f(euler_particle.position,
                                                                           euler_particle.velocity))
    # Create particle that will be used to test beeman
    beeman_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0,
                               o=0.0)
    beeman_particle.previous_acceleration = initial_previous_acceleration(beeman_particle, delta_t,
                                                                          f(beeman_particle.position,
                                                                            beeman_particle.velocity))

    # Create particle that will be used to test verlet
    verlet_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M, v=constants.V0,
                               o=0.0)

    # Create particle that will be used to test gear predictor
    gear_predictor_particle = Particle(x=constants.X0, y=constants.Y0, radius=constants.R, mass=constants.M,
                                       v=constants.V0,
                                       o=0.0)
    return real_particle, euler_particle, beeman_particle, verlet_particle, gear_predictor_particle

# noinspection PyPep8Naming
def f(position, velocity):
    return (-K * position) - (lamb * velocity)


# ----------------------------------------------------------------------------------------------------------------------
#       MAIN
# ----------------------------------------------------------------------------------------------------------------------



delta_t = 0.001

real_particle, euler_particle, beeman_particle, verlet_particle, gear_predictor_particle = generate_particles()

times, positions_real, positions_euler, positions_beeman, positions_verlet, positions_gear_predictor = [], [], [], [], [], []

euler_error, beeman_error, verlet_error, gear_error = 0, 0, 0, 0

iteration = 0

MAX_TIME = 4

for t in np.arange(0, MAX_TIME, delta_t):
    iteration += 1
    times.append(t)
    real_x = real.x(t)
    positions_real.append(real_x)

    # Calculate euler particle new position
    if "euler" in args.integration_method or "all" in args.integration_method:
        euler_force = f(euler_particle.position, euler_particle.velocity)
        euler_x = euler_modified.x(particle=euler_particle, delta_t=delta_t, force=euler_force)
        positions_euler.append(euler_x.x)
        euler_particle.position = euler_x
        euler_particle.velocity = euler_modified.v(particle=euler_particle, delta_t=delta_t, force=euler_force)
        euler_error += (euler_x[0] - real_x) ** 2

    # Calculate beeman particles new position
    if "beeman" in args.integration_method or "all" in args.integration_method:
        current_acceleration = beeman_particle.acceleration
        beeman_force = f(beeman_particle.position, beeman_particle.velocity)
        beeman_particle.acceleration = beeman_force / beeman_particle.mass
        beeman_x = beeman.r(particle=beeman_particle, delta_t=delta_t)
        positions_beeman.append(beeman_x.x)
        beeman_particle.position = beeman_x
        beeman_particle.velocity = beeman.v(particle=beeman_particle, delta_t=delta_t, force=beeman_force, f=f)
        beeman_particle.previous_acceleration = current_acceleration
        beeman_error += (beeman_x[0] - real_x) ** 2

    # Calculate verlet particle new position
    if "verlet" in args.integration_method or "all" in args.integration_method:
        verlet_force = f(verlet_particle.position, verlet_particle.velocity)
        verlet_x = verlet.r(particle=verlet_particle, delta_t=delta_t, force=verlet_force)
        positions_verlet.append(verlet_x.x)
        verlet_particle.position = verlet_x
        verlet_particle.velocity = verlet.v(particle=verlet_particle, delta_t=delta_t, force=verlet_force)
        verlet_error += (verlet_x[0] - real_x) ** 2

    # Calculate gear predictor particle new position
    if "gear" in args.integration_method or "all" in args.integration_method:
        gear_predictor_derivatives = gear_predictor.run(particle=gear_predictor_particle, delta_t=delta_t)
        positions_gear_predictor.append(gear_predictor_derivatives[0].x)
        gear_predictor_particle.position = gear_predictor_derivatives[0]
        gear_predictor_particle.velocity = gear_predictor_derivatives[1]
        gear_error += (gear_predictor_derivatives[0].x - real_x) ** 2

plt.plot(times, positions_real, 'r:', label="Analítico")

print("Mean Quadratic Errors")

# Check parameters to see what to graph
if "euler" in args.integration_method or "all" in args.integration_method:
    plt.plot(times, positions_euler, 'c:', label="Euler")
    print("Euler: %g" % (euler_error / iteration))

if "beeman" in args.integration_method or "all" in args.integration_method:
    plt.plot(times, positions_beeman, 'm:', label="Beeman")
    print("Beeman: %g" % (beeman_error / iteration))

if "verlet" in args.integration_method or "all" in args.integration_method:
    plt.plot(times, positions_verlet, 'b:', label="Verlet")
    print("Verlet: %g" % (verlet_error / iteration))

if "gear" in args.integration_method or "all" in args.integration_method:
    plt.plot(times, positions_gear_predictor, 'g:', label="Gear predictor 5")
    print("Gear Predictor: %g" % (gear_error / iteration))

plt.legend()

plt.ylabel('Amplitud [m]')
plt.xlabel('Tiempo [s]')
plt.title('Oscilador Amortiguado')
plt.show()
