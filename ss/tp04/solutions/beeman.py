from ss.cim.particle import Particle
from ss.tp04.solutions import euler_modified


def r(particle, delta_t, force):
    return particle.position + particle.velocity*delta_t+((2/3)*particle.acceleration - (1/6)*particle.previous_acceleration)*delta_t**2


def v_predicted(particle, delta_t):
    return particle.velocity + (3/2)*particle.acceleration*delta_t \
           - 0.5*particle.previous_acceleration*delta_t


def v_corrected(particle, delta_t, next_acceleration):
    return particle.velocity + (1/3) * next_acceleration * delta_t + (5 / 6) * particle.acceleration * delta_t \
           - (1/6)*particle.previous_acceleration*delta_t


def v(particle, delta_t, force, f):
    predicted_velocity = v_predicted(particle, delta_t)
    predicted_position = r(particle, delta_t, force)

    vel, angle = Particle.to_v_o(predicted_velocity)
    predicted_particle = Particle(predicted_position[0], predicted_position[1], particle.radius, particle.mass, vel, angle, is_fake=True)

    predicted_acceleration = f(predicted_position, predicted_velocity) / predicted_particle.mass

    return v_corrected(particle, delta_t, predicted_acceleration)
