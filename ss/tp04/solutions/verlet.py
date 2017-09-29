from ss.tp04.oscillator.constants import *
from ss.tp04.solutions import euler_modified


def r(particle, delta_t, force):
    return 2*particle.position - previous_position(particle, delta_t, force) + (delta_t ** 2 / particle.mass) * force


def v(particle, delta_t, force):
    return (r(particle, delta_t, force) - particle.previous_position) / (2 * delta_t)


def previous_position(particle, delta_t, force):
    """Get the particle's previous position or use Euler to simulate backwards to where it would have been"""

    result = particle.previous_position
    if result is None:
        # We're in initial step, use Euler to simulate backwards
        result = euler_modified.x(particle, -delta_t, force)
    return result
