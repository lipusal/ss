from math import sqrt
from uuid import uuid4 as uuid
from euclid3 import Vector2


class Particle:
    """Model class for particles used in simulations"""

    def __init__(self, x, y, radius=0):
        self._id = uuid().int
        self.radius = radius
        self.position = Vector2(x, y)
        self.velocity = Vector2()
        # TODO usar vectores de velocidad

    def move_to(self, x, y):
        self.position = Vector2(x, y)

    def distance_to(self, other):
        # centerDistance = sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
        center_distance = abs(other.position - self.position)
        return center_distance - self.radius - other.radius

    @property
    def id(self):
        return self._id

    def __str__(self) -> str:
        return "Particle (%g, %g)" % (self.position.x, self.position.y)
