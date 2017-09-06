import math
from ss.util.ddict import Ddict
from collections import defaultdict
from ss.cim.cell import Cell


class CellIndexMethod:
    def __init__(self, particles, args):
        self.particles = particles
        self.interaction_radius = args.radius
        self.is_periodic = args.periodic if 'periodic' in args else False
        self.width = args.l if 'l' in args and args.l is not None else -1
        # TODO: Change arg names
        self.height = args.h if 'h' in args and args.h is not None else -1
        self.m = args.m if 'm' in args and args.m is not None else -1
        self.board = [[]]
        self.particles_in_cells()
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

        l = max(self.width, self.height)
        if self.width == -1 or self.height == -1 or self.m == -1:
            # Calculate minimum bounding rectangle for particles
            xs, ys = [], []
            max_radius = 0
            for particle in self.particles:
                xs.append(particle.x)
                ys.append(particle.y)
                max_radius = max((max_radius, particle.radius))

            # Compute optimal board parameters
            width, height = max(xs), max(ys)    # TODO: If min(xs) >> 0 we will have a lot of empty space; ídem ys
            if self.width == -1:
                self.width = width
            if self.height == -1:
                # If height not provided, assume square board unless the particles would end up outside the board
                self.height = max(self.width, height)

            # Quick fix to prevent out-of-range bugs when particles are at EXACTLY the board limit
            epsilon = 1e-5
            self.width += epsilon
            self.height += epsilon

            # Recalculate in case width or height were -1 before
            l = max(self.width, self.height)

            if self.m == -1:
                # Compute optimal board parameters
                self.m = math.ceil(l / (self.interaction_radius + 2 * max_radius))
                if l / self.m <= self.interaction_radius:
                    # FIXME: This shouldn't happen, revise previous formula
                    print("WARNING: The calculated M (%i) is over limit, restricting to " % self.m, end="")
                    self.m = math.floor(l / self.interaction_radius) - 1
                    print(self.m)

        if l / self.m <= self.interaction_radius:
            raise Exception("L / M > Rc is not met, can't perform cell index method, aborting. (L = %g, M = %g, "
                            "Rc = %g)" % (l, self.m, self.interaction_radius))

        # Create board and put particles in it
        self.board = self.create_board(self.width, self.height, l / self.m)
        for particle in self.particles:
            row, col = self.get_cell(particle)
            self.board[row][col].particles.append(particle)

    def get_cell(self, particle):
        """Gets the cell to which a given particle belongs in the current board"""

        # TODO: Ensure that when the board is periodic and width or height are not a multiple of M, the part of the cell
        # TODO: that may be uncovered is never used; the particle should go around immediately

        row, col = int(particle.y / self.height * self.num_rows()), int(particle.x / self.width * self.num_cols())
        if self.is_periodic:
            row %= self.num_rows()
            col %= self.num_cols()
        elif not 0 <= row < self.m or not 0 <= col < self.m:
                raise Exception("%s is outside the board, and board is not periodic; max valid coordinates are (%g, %g)"
                                % (particle, self.width, self.height))

        return row, col  # Return array indices rather than raw (x,y)

    # list with distances of particle with id to its corresponding neighbors
    def get_distances(self, id):
        return [x[1] for x in self.neighbors[id]]

    def create_board(self, width, height, cell_side_length):
        """Creates a board of the given size, filling each dimension with as many cells are needed"""

        board = []
        for y in range(int(math.ceil(height / cell_side_length))):
            board.append([])
            for x in range(int(math.ceil(width / cell_side_length))):
                board[y].append(Cell(y, x))

        return board

    def num_rows(self):
        return len(self.board)

    def num_cols(self):
        return len(self.board[0])

    def __str__(self):
        result = ""
        for row in reversed(range(self.num_rows())):
            result += '|'
            for col in range(self.num_cols()):
                result += "%i|" % len(self.board[row][col].particles)
            result += "\n"
        return result
