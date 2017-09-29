from ss.tp04.oscillator.constants import *
from ss.tp04.oscillator.solutions import euler_modified


def x(delta_t, particle):
    previous_position = particle.previous_position
    if previous_position is None:
        # We're in initial step, use Euler to simulate backwards
        previous_position = euler_modified.x(-delta_t, particle)

    return 2*particle.position - previous_position + (delta_t**2 / particle.mass) * F(particle)


# noinspection PyPep8Naming
def F(particle):
    return (-K * particle.position) - (lamb * particle.velocity)
