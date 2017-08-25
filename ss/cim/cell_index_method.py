from math import ceil
from ss.util.ddict import Ddict
from collections import defaultdict
from ss.cim.cell import Cell


class CellIndexMethod:
    def __init__(self, particles, args):
        self.particles = particles
        self.interaction_radius = args.radius
        self.is_periodic = args.periodic if 'periodic' in args else False
        self.l = args.l if 'l' in args and args.l is not None else -1
        self.cells_per_row = args.m if 'm' in args and args.m is not None else -1
        self.board = self.particles_in_cells()
        self.neighbors = self.calculate_neighbors()

    def calculate_distances(self):
        result = Ddict.ddict()  # Dictionary that returns a new dictionary when accessing a nonexistent key
        for row in self.board:
            for cell in row:
                for me in cell.particles:
                    for neighbor in cell.getNeighborParticles(self):
                        if me == neighbor or neighbor in result[me.id]:
                            continue

                        distance = me.distance_to(neighbor)
                        result[me.id][neighbor.id] = result[neighbor.id][me.id] = distance

        return Ddict.to_dict(result)

    def calculate_neighbors(self):
        result = defaultdict(list)
        for row in self.board:
            for cell in row:
                for me in cell.particles:
                    for neighbor in cell.getNeighborParticles(self):
                        if me == neighbor or neighbor in result[me.id]:
                            continue
                        distance = me.distance_to(neighbor)
                        if distance <= self.interaction_radius:
                            # Put only real particles in result
                            result[me.id].append(
                                (neighbor.original_particle if neighbor.is_fake else neighbor, distance))
                            result[neighbor.original_particle.id if neighbor.is_fake else neighbor.id].append(
                                (me, distance))
        # Don't convert to plain dict because caller doesn't know which particles have neighbors and which don't. Keep
        # behavior of returning empty list when accessing a new key (doesn't contemplate invalid keys though, those will
        # also return empty list)
        return result

    def particles_in_cells(self):
        """If side_length and cells_per_row are both not -1, creates a corresponding board with cells. Otherwise,
        calculates a minimum bounding rectangle that contains the specified particles, and calculates the side length
        and number of cells per row. In either case, places all particles in their corresponding cell."""

        if self.l == -1 or self.cells_per_row == -1:
            # Calculate minimum bounding rectangle for particles
            xs, ys = [], []
            max_radius = 0
            for particle in self.particles:
                xs.append(particle.x)
                ys.append(particle.y)
                max_radius = max((max_radius, particle.radius))

            # Compute optimal board parameters

            # Quick fix to prevent bugs when particles are at EXACTLY the board limit
            epsilon = 1e-5
            width, height = ceil(max(xs)) + epsilon, ceil(max(ys)) + epsilon
            if self.l == -1:
                self.l = max((width, height))
            if self.cells_per_row == -1:
                # TODO support rectangular boards?
                self.cells_per_row = int(ceil(self.l / (self.interaction_radius + 2 * max_radius)))

        # if self.l / self.cells_per_row <= self.interaction_radius:
        #     raise Exception("L / M > Rc is not met, can't perform cell index method, aborting. (L = %g, M = %g, "
        #                     "Rc = %g)" % (self.l, self.cells_per_row, self.interaction_radius))

        # Create board and put particles in it
        board = self.create_board(self.cells_per_row, self.cells_per_row)
        for particle in self.particles:
            row, col = self.get_cell(particle)
            board[row][col].particles.append(particle)

        return board

    def get_cell(self, particle):
        """Gets the cell to which a given particle belongs in the current board"""

        row, col = int(particle.y / self.l * self.cells_per_row), int(particle.x / self.l * self.cells_per_row)
        return row, col  # Return array indices rather than raw (x,y)

    # list with distances of particle with id to its corresponding neighbors
    def get_distances(self, id):
        return [x[1] for x in self.neighbors[id]]

    def create_board(self, width, height):
        board = []
        for y in range(height):  # TODO: Support rectangular boards?
            board.append([])
            for x in range(width):
                board[y].append(Cell(y, x))

        return board

    def __str__(self):
        result = ""
        for row in reversed(range(self.cells_per_row)):
            result += '|'
            for col in range(self.cells_per_row):
                result += "%i|" % len(self.board[row][col].particles)
            result += "\n"
        return result
