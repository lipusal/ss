import math
from ss.tp04.oscillator.constants import *

DEGREE = 5

# 5th-degree Gear Predictor coefficients for forces that depend on R0, R1 (ie. position & velocity,
# as in the oscillator)
ALPHAS_RV = [3 / 16, 251 / 360, 1, 11 / 18, 1 / 6, 1 / 60]


def x(particle, delta_t):
    return run(particle, delta_t)[0]


def v(particle, delta_t):
    return run(particle, delta_t)[1]


def run(particle, delta_t):
    """Runs the whole predict-evaluate-correct process and returns the five corrected derivatives"""

    r_ps = predict(particle, delta_t)
    delta_r2 = evaluate(particle, delta_t, r_ps)
    result = correct(r_ps, ALPHAS_RV, delta_r2, delta_t)
    return result


def predict(particle, delta_t):
    """Predict the 5 derivatives of the position for the given delta T, using the original 5 derivatives."""

    result = [0] * (DEGREE + 1)
    rs = rs_oscillator(particle)
    for i in range(DEGREE, -1, -1):
        result[i] = rs[i]
        k = 1
        for j in range(i+1, DEGREE+1):
            result[i] += rs[j]*(delta_t**k)/math.factorial(k)
            k += 1

    return result


def evaluate(particle, delta_t, r_ps):
    # Evaluate R2 in RP0, RP1 (predicted position, predicted velocity) -- this is specific to the oscillator
    a = ((r_ps[0] * -K) - r_ps[1] * lamb) / particle.mass
    delta_a = a - r_ps[2]

    return delta_a * (delta_t**2) / math.factorial(2)   # Delta R2


def correct(r_ps, alphas, delta_r2, delta_t):
    result = [0] * (DEGREE + 1)
    for i in range(DEGREE + 1):
        result[i] = r_ps[i] + alphas[i] * delta_r2 * (math.factorial(i) / (delta_t**i))

    return result


def rs_oscillator(particle):
    """Calculate the 5 derivatives of the oscillator's position (R's in the Gear Predictor)"""

    result = [particle.position, particle.velocity]     # R0, R1
    for i in range(2, DEGREE+1):   # R2, R3, R4, R5
        result.append(((result[i-2] * -K) - result[i-1] * lamb) / particle.mass)
    return result
