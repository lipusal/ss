from ss.cim.particle import Particle
from ss.tp04.solutions import euler_modified


def x(particle, delta_t, f):
    return particle.position + particle.velocity*delta_t+((2/3)*particle.acceleration - (1/6)*previous_acceleration(particle, delta_t, f))*delta_t**2

def v_predicted(particle, delta_t, f):
    return particle.velocity + (3/2)*particle.acceleration*delta_t \
           - 0.5*previous_acceleration(particle, delta_t, f)*delta_t

def v_corrected(particle, delta_t, f, next_acceleration):
    return particle.velocity + (1/3) * next_acceleration * delta_t + (5 / 6) * particle.acceleration * delta_t \
           - (1/6)*previous_acceleration(particle, delta_t, f)*delta_t

def v(particle, delta_t, f):
    predicted_v = v_predicted(particle,delta_t,f)
    v, o = Particle.to_v_o(predicted_v)
    predicted_particle = Particle(x=particle.position.x, y=particle.position.y, radius=particle.radius, v=v, mass=particle.mass, o=o, is_fake=True)
    acceleration = f(predicted_particle.position, predicted_particle.velocity)/particle.mass
    return v_corrected(particle, delta_t, f, acceleration)

def previous_acceleration(particle, delta_t, f):
    """Get the particle's previous position or use Euler to simulate backwards to where it would have been"""

    prev_acceleration = particle.previous_acceleration
    if prev_acceleration is None:
        # We're in initial step, use Euler to simulate backwards
        vel = euler_modified.v(particle, -delta_t)
        prev_acceleration = f(particle.position, vel) / particle.mass
    return prev_acceleration