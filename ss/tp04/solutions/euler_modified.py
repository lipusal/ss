from ss.tp04.oscillator.constants import *


def x(particle, delta_t):
    return particle.position + delta_t * v(particle, delta_t) + (delta_t ** 2 / (2 * particle.mass)) * f(particle)


def v(particle, delta_t):
    return particle.velocity + (delta_t / particle.mass) * f(particle)


# noinspection PyPep8Naming
def f(particle):
    return (-K * particle.position) - (lamb * particle.velocity)
