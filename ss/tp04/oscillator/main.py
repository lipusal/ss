import matplotlib.pyplot as plt
import numpy as np

import ss.util.args as arg_base
from ss.tp04.oscillator.constants import *
from ss.tp04.solutions import real

# TODO: Update description
arg_base.parser.description = "Gas Diffusion simulation Program. Simulates how a number of given gas particles diffuse " \
                          "from one compartment to another through a slit"
args = arg_base.parse_args()

# TODO: Set X function according to params
x = real.x


# noinspection PyPep8Naming
def F(t):
    return (-K * x(t)) - (lamb * X0)


# ----------------------------------------------------------------------------------------------------------------------
#       MAIN
# ----------------------------------------------------------------------------------------------------------------------

times, positions = [], []
for t in np.arange(0, 10, 0.01):
    times.append(t)
    positions.append(x(t))
    print("x(%g) = %g" % (times[-1], positions[-1]))

plt.plot(times, positions)
plt.show()
