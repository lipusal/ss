from math import sqrt

class Particle:
    '''Model class for particles used in simulations'''

    def __init__(self, x, y, radius = 0):
        self.radius = radius
        self.moveTo(x, y)

    def moveTo(self, x, y):
        self.x = x
        self.y = y

    def distanceTo(self, other):
        centerDistance = sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
        return centerDistance - self.radius - other.radius

    def __str__(self) -> str:
        return "Particle (%g, %g)" % (self.x, self.y)
