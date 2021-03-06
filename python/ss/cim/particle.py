import math
import random

from euclid3 import Vector2


class Particle:
    """Model class for particles used in simulations"""

    _global_id = 1

    def __init__(self, x, y, radius=0.0, mass=0.0, v=0.0, o=0.0, is_fake=False, original_particle=None, id=None):
        if id is None:
            self._id = Particle._global_id
            Particle._global_id += 1
        else:
            self._id = id

        self.radius = radius
        self._position = Vector2(x, y)
        self._velocity = self.to_x_y(v, o)
        self._acceleration = self.to_x_y(0, 0)
        self.mass = mass
        self.is_fake = is_fake
        self.original_particle = original_particle
        self.previous_position = None
        self.previous_velocity = None
        self.previous_acceleration = None
        if not original_particle is None and not self.is_fake:
            raise Exception("Can't have original particle and not be fake")

    def move_to(self, x, y):
        """Moves this particle to the specified position. Stores current position in previous_position property."""

        self._position = Vector2(x, y)

    def move(self, delta_x, delta_y):
        """Moves this particle the specified amounts in X and Y from its current position"""

        self.move_to(self.x + delta_x, self.y + delta_y)

    def distance_to(self, other):
        # centerDistance = sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
        center_distance = (other.position - self.position).magnitude()
        return center_distance - self.radius - other.radius

    # Returns a particle with a random position in the given space, and a random direction.
    @classmethod
    def get_random_particle(cls, max_height, max_width, radius, speed, mass=0.0, min_height=0.0, min_width=0.0):
        x = random.uniform(min_width+radius, max_width - radius)
        y = random.uniform(min_height+radius, max_height - radius)
        o = random.uniform(0.0, 2 * math.pi)
        return cls(x=x, y=y, radius=radius, mass=mass, v=speed, o=o, is_fake=False, original_particle=None)

    @property
    def id(self):
        return self._id

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self.previous_position = self._position
        self._position = value

    @property
    def x(self):
        return self._position.x

    @property
    def y(self):
        return self._position.y

    def relative_position(self, other):
        """Return other.position - self.position (ie. position relative to self)"""
        return other.position - self.position

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        """Sets velocity. Value should be a tuple of the form `(mod, angle)`. Stores current velocity in
        previous_velocity property."""

        self.previous_velocity = self._velocity
        self._velocity = self.to_x_y(value[0], value[1])

    def relative_velocity(self, other):
        """Return other.velocity - self.velocity (ie. relative to self)"""
        return other.velocity - self.velocity

    @property
    def acceleration(self):
        return self._acceleration

    @acceleration.setter
    def acceleration(self, value):
        self.previous_acceleration = self.acceleration
        self._acceleration = value

    # @property
    def mass(self):
        return self.mass

    def vel_angle(self):
        """Returns the angle of the particle's velocity"""
        # return math.atan(self._velocity.y / self._velocity.x)
        return math.atan2(self._velocity.y, self._velocity.x)

    def vel_module(self):
        return self.velocity.magnitude()

    @staticmethod
    def to_x_y(mod, deg):
        """Constructs a vector with a given modulus and angle (converts to (x,y))"""
        return Vector2(math.cos(deg)*mod, math.sin(deg)*mod)

    @staticmethod
    def to_v_o(v):
        return abs(v), math.atan2(v.y, v.x)

    def __str__(self) -> str:
        return "%sParticle #%i @ (%g, %g), r = %g" % ("Fake " if self.is_fake else "", self.id, self._position.x, self._position.y, self.radius)
