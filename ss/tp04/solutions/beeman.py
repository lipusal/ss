def x(particle, delta_t):
    return particle.position + particle.velocity*delta_t + (1/6)*(4*particle.acceleration
            - particle.previous_acceleration)*delta_t**2

def v_predicted(particle, delta_t):
    return particle.velocity + (3/2)*particle.acceleration*delta_t \
           - 0.5*particle.previous_acceleration*delta_t

def v_corrected(particle, delta_t, prox_acceleration):
    return particle.velocity + (1/3)*prox_acceleration*delta_t + (5/6)*particle.acceleration*delta_t \
           - (1/6)*particle.previous_acceleration*delta_t

def v(particle, delta_t, prox_acceleration):
    return particle.velocity + ((1/3)*prox_acceleration + (5/6)*particle.acceleration
            - (1/6)*particle.previous_acceleration)*delta_t