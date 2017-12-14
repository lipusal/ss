from enum import Enum

from euclid3 import Vector2

Direction = Enum('Direction', 'NORTH SOUTH EAST WEST')


class Car:

    _global_id = 1

    def __init__(self, acceleration, x, y, length, vx=0, vy=0, id=None):
        if id is None:
            self._id = Car._global_id
            Car._global_id += 1
        else:
            self._id = id
        self.direction = Direction.EAST
        self.bk = False
        self.velocity = Vector2(vx, vy)
        self.acceleration = acceleration
        self.position = Vector2(x,y)
        self.length = length

    def distance_to(self, other_car):
        if self.direction == Direction.EAST or self.direction == Direction.WEST:
            return abs(other_car.position.x - self.position.x)
        elif self.direction == Direction.SOUTH or self.direction.NORTH:
            return abs(other_car.position.y - self.position.y)

    def turn_on_lights(self):
        self.bk = True

    def turn_off_lights(self):
        self.bk = False

    def has_lights_on(self):
        return self.bk

    def move_by(self, dist, road_length):

        if self.position.x + dist >= road_length and self.direction == Direction.EAST:
            self.position.x = self.position.x + dist - road_length

        elif self.direction == Direction.EAST:
            self.position.x += dist
        elif self.direction == Direction.WEST:
            self.position.x -= dist
        elif self.direction == Direction.NORTH:
            self.position.y += dist
        elif self.direction == Direction.SOUTH:
            self.position.y -= dist

    @property
    def id(self):
        return self._id

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y