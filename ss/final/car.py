from euclid3 import Vector2


class Car:

    def __init__(self, velocity, acceleration, x, y):
        self.bk = False
        self.velocity = velocity
        self.acceleration = acceleration
        self.position = Vector2(x,y)
