from math import sqrt
from uuid import uuid4 as uuid
from euclid3 import Vector2


class Particle:
    """Model class for particles used in simulations"""

    _global_id = 1

    def __init__(self, x, y, radius=0.0, is_fake=False, original_particle=None):
        self._id = Particle._global_id
        Particle._global_id += 1
        self.radius = radius
        self.position = Vector2(x, y)
        self.velocity = Vector2()
        self.is_fake = is_fake
        self.original_particle = original_particle
        if not original_particle is None and not self.is_fake:
            raise Exception("Can't have original particle and not be fake")
        # TODO usar vectores para velocidad

    def move_to(self, x, y):
        self.position = Vector2(x, y)

    def distance_to(self, other):
        # centerDistance = sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
        center_distance = abs(other.position - self.position)
        return center_distance - self.radius - other.radius

    @property
    def id(self):
        return self._id

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    def __str__(self) -> str:
        return "%sParticle #%i @ (%g, %g), r = %g" % ("Fake " if self.is_fake else "", self.id, self.position.x, self.position.y, self.radius)
