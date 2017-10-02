import math
from ss.cim.cell import Cell


class Board:

    # Used to give a little extra room to boards to prevent out-of-board errors when particles are at EXACTLY the board
    #limit
    EPSILON = 1e-5

    def __init__(self, particles, **kwargs):
        self.particles = particles
        self.width = kwargs.get('width')
        self.height = kwargs.get('height')
        self.cell_side_length = kwargs.get('cell_side_length')
        self.is_periodic = kwargs.get('is_periodic', False)
        self.num_cols = int(math.ceil(self.width / self.cell_side_length))
        self.num_rows = int(math.ceil(self.height / self.cell_side_length))
        self.cells = self.create_board()
        self.populate()

    def to_col_row(self, x, y):
        """Converts an (X, Y) coordinate to a (row, col) coordinate within this board."""

        row, col = int(y / self.height * self.num_rows), int(x / self.width * self.num_cols)
        if self.is_periodic:
            row %= self.num_rows
            col %= self.num_cols
        elif not 0 <= row < self.num_rows or not 0 <= col < self.num_cols:
            raise Exception("(%g, %g) is outside the board, and board is not periodic; max valid coordinates are "
                            "(%g, %g)" % (x, y, self.width, self.height))

        return col, row

    def get_cell(self, particle):
        if particle not in self.particles:
            raise Exception("%s is not part of this board" % particle)
        if particle.x < 0 or particle.y < 0 or particle.x> self.width or particle.y > self.height:
            raise Exception("%s is outside the board bounds" %particle)
        return self.to_col_row(particle.x, particle.y)

    def create_board(self):
        """Creates a board of this instance's size, filling each dimension with as many cells as are needed"""

        self.cells = [[]] * self.num_rows
        for y in range(self.num_rows):
            for x in range(int(math.ceil(self.width / self.cell_side_length))):
                self.cells[y].append(Cell(y, x))

        return self.cells

    def populate(self):
        """Populates cells with the particles self was initialized with."""

        for particle in self.particles:
            assert particle.x > 0 and particle.y >0 and particle.x < self.width and particle.y < self.height
            col, row = self.get_cell(particle)
            self.cells[row][col].particles.append(particle)

        return self

    def calculate_mbb(self):
        """Calculates minimum bounding box for this instance's particles"""

        return Board.calculate_mbb(self.particles)

    @staticmethod
    def calculate_mbb(particles):
        """Calculates minimum bounding box for a given list of particles. Returns (width, height)"""

        xs, ys = [], []
        for particle in particles:
            xs.append(particle.x)
            ys.append(particle.y)

        # TODO: If min(xs) >> 0, will have a lot of empty space; ídem ys
        return max(xs) + Board.EPSILON, max(ys) + Board.EPSILON
