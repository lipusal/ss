from ss.tp04.oscillator.constants import *


def x(delta_t, particle):
    return particle.position + delta_t * v(delta_t, particle) + (delta_t**2 / (2*particle.mass))*F(particle)


def v(delta_t, particle):
    return particle.previous_velocity + (delta_t / particle.mass) * F(particle)


# noinspection PyPep8Naming
def F(particle):
    return (-K * particle.position) - (lamb * particle.velocity)
