from ss.cim.particle import Particle
from ss.tp04.solutions import euler_modified


def x(particle, delta_t, force):
    return particle.position + particle.velocity*delta_t+((2/3)*particle.acceleration - (1/6)*particle.previous_acceleration)*delta_t**2


def v_predicted(particle, delta_t):
    return particle.velocity + (3/2)*particle.acceleration*delta_t \
           - 0.5*particle.previous_acceleration*delta_t


def v_corrected(particle, delta_t, next_acceleration):
    return particle.velocity + (1/3) * next_acceleration * delta_t + (5 / 6) * particle.acceleration * delta_t \
           - (1/6)*particle.previous_acceleration*delta_t


def v(particle, delta_t, force):
    predicted_v = v_predicted(particle, delta_t)
    v, o = Particle.to_v_o(predicted_v)
    predicted_particle = Particle(x=particle.position.x, y=particle.position.y, radius=particle.radius, v=v, mass=particle.mass, o=o, is_fake=True)
    acceleration = force/particle.mass
    return v_corrected(particle, delta_t, acceleration)
