import math
import colorsys

def radians_to_rgb(theta):
    """Converts an angle (in radians, (-pi, pi]) to a color using the HSV scale, and converts that to an RGB color
    which is compatible with Ovito"""

    # HSV -> RGB function requires values between 0 and 1, so map -pi < theta <= pi to 0 <= theta <= 1
    # https://stackoverflow.com/questions/345187/math-mapping-numbers#comment36962941_345204
    mapped_theta = (theta + math.pi) / (math.pi + math.pi)
    return colorsys.hsv_to_rgb(mapped_theta, 1, 1)
