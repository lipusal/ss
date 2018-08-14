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
    """Predict the 5 derivatives of the position for the given delta T, using the original 5 derivatives.
    rP[5] (t + Δt) = r[5](t)
    rP[4] (t + Δt) = r[4](t) + r[5](t) * Δt^1 / 1!
    rP[3] (t + Δt) = r[3](t) + r[4](t) * Δt^2 / 2!
    ...
    """

    result = [0] * (DEGREE + 1)
    rs = rs_oscillator(particle)
    for i in range(DEGREE, -1, -1):
        # debug = "rP[%i](t+Δt) = r[%i](t)" % (i, i)
        result[i] = rs[i]
        k = 1
        for j in range(i+1, DEGREE+1):
            result[i] += rs[j]*(delta_t**k)/math.factorial(k)
            # debug += " + r[%i]*Δt^%i/%i!" % (j, k, k)
            k += 1

        # print(debug)

    return result


def evaluate(particle, delta_t, r_ps):
    # Evaluate r[2] in rP[0], rP[1] (predicted position, predicted velocity) to get future acceleration
    delta_a = r2_oscillator(particle, r_ps) - r_ps[2]

    return delta_a * (delta_t**2) / math.factorial(2)   # Delta R2


def correct(r_ps, alphas, delta_r2, delta_t):
    result = list()
    for i in range(DEGREE + 1):
        result.append(r_ps[i] + (alphas[i] * delta_r2 * math.factorial(i) / (delta_t**i)))

    return result


def rs_oscillator(particle):
    """Calculate the 5 derivatives of the oscillator's position (R's in the Gear Predictor). This is specific to the
    oscillator."""

    result = [particle.position, particle.velocity]     # R0, R1
    # For oscillator, for every n >= 2, r[n] = (K * r[n-2] + lambda * r[n-1]) / -mass
    # K = 1
    for n in range(2, DEGREE + 1):  # R2, R3, R4, R5
        result.append((K * result[n - 2] + lamb * result[n - 1]) / -particle.mass)
    return result



def r2_oscillator(particle, r_ps):
    """Get future acceleration of an oscillator with the given current state and predicted future derivatives. This is
    specific to the oscillator."""

    # r[2] = (K*r[0] + lambda*r[1]) / -mass (see `rs_oscillator`)
    return (K*r_ps[0] + lamb*r_ps[1]) / -particle.mass
