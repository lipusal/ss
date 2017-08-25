import math
from euclid3 import Vector2


class Particle:
    """Model class for particles used in simulations"""

    _global_id = 1

    def __init__(self, x, y, radius=0.0, v=0.0, o=0.0, is_fake=False, original_particle=None):
        self._id = Particle._global_id
        Particle._global_id += 1
        self.radius = radius
        self._position = Vector2(x, y)
        self._velocity = self.to_x_y(v, o)
        self.is_fake = is_fake
        self.original_particle = original_particle
        if not original_particle is None and not self.is_fake:
            raise Exception("Can't have original particle and not be fake")

    def move_to(self, x, y):
        self._position = Vector2(x, y)

    def distance_to(self, other):
        # centerDistance = sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
        center_distance = abs(other._position - self._position)
        return center_distance - self.radius - other.radius

    @property
    def id(self):
        return self._id

    @property
    def x(self):
        return self._position.x

    @property
    def y(self):
        return self._position.y

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        """Sets velocity. Value should be a tuple of the form `(mod, angle)`"""

        self._velocity = self.to_x_y(value[0], value[1])

    def vel_angle(self):
        """Returns the angle of the particle's velocity"""
        # return math.atan(self._velocity.y / self._velocity.x)
        return math.atan2(self._velocity.y, self._velocity.x)

    @staticmethod
    def to_x_y(mod, deg):
        """Constructs a vector with a given modulus and angle (converts to (x,y))"""
        return Vector2(math.cos(deg)*mod, math.sin(deg)*mod)

    def __str__(self) -> str:
        return "%sParticle #%i @ (%g, %g), r = %g" % ("Fake " if self.is_fake else "", self.id, self._position.x, self._position.y, self.radius)
