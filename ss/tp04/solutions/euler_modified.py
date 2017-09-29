from ss.tp04.oscillator.constants import *


def x(particle, delta_t, force):
    return particle.position + delta_t * v(particle, delta_t, force) + (delta_t ** 2 / (2 * particle.mass)) * force


def v(particle, delta_t, force):
    return particle.velocity + (delta_t / particle.mass) * force
