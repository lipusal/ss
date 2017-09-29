from ss.tp04.oscillator.constants import *
from ss.tp04.solutions import euler_modified


def x(particle, delta_t):
    return 2*particle.position - previous_position(particle, delta_t) + (delta_t ** 2 / particle.mass) * f(particle)


def v(particle, delta_t):
    return (x(particle, delta_t) - previous_position(particle, delta_t)) / (2 * delta_t)


def f(particle):
    return (-K * particle.position) - (lamb * particle.velocity)


def previous_position(particle, delta_t):
    """Get the particle's previous position or use Euler to simulate backwards to where it would have been"""

    result = particle.previous_position
    if result is None:
        # We're in initial step, use Euler to simulate backwards
        result = euler_modified.x(particle, -delta_t)
    return result
