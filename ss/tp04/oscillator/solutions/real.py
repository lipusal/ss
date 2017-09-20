import math
from ss.tp04.oscillator.constants import *


def x(t):
    return math.exp(-(lamb / (2*M)) * t) * math.cos(math.sqrt((K/M) - (lamb**2 / (4*M**2))) * t)
