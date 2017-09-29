from ss.tp04.oscillator.constants import *


def x(delta_t, particle):
    return particle.position + delta_t * v(delta_t, particle) + (delta_t**2 / (2*particle.mass)) * f(particle)


def v(delta_t, particle):
    return particle.velocity + (delta_t / particle.mass) * f(particle)


# noinspection PyPep8Naming
def f(particle):
    return (-K * particle.position) - (lamb * particle.velocity)
