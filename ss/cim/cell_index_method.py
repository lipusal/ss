from math import ceil
from ss.util.ddict import Ddict
from collections import defaultdict
from ss.cim.particle import Particle


class CellIndexMethod:
    def __init__(self, *particles, interaction_radius, is_periodic=False):
        self.particles = particles
        self.interaction_radius = interaction_radius
        self.is_periodic = is_periodic
        self.l = -1
        self.cells_per_row = -1
        self.board = self.particles_in_cells(particles, interaction_radius)
        self.distances = self.calculate_distances() # TODO stop using this, it's only used for debugging
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
                            result[me.id].append(neighbor)
                            result[neighbor.id].append(me)
        # Don't convert to plain dict because caller doesn't know which particles have neighbors and which don't. Keep
        # behavior of returning empty list when accessing a new key (doesn't contemplate invalid keys though, those will
        # also return empty list)
        return result

    def particles_in_cells(self, particles, interaction_radius):
        """Calculates a minimum bounding rectangle that contains the specified particles, calculates the optimum number
        of cells per row, and places all particles in their corresponding cell."""

        # Calculate minimum bounding rectangle for particles
        xs, ys = [], []
        max_radius = 0
        for particle in particles:
            xs.append(particle.x)
            ys.append(particle.y)
            max_radius = max((max_radius, particle.radius))

        # Compute optimal board parameters
        width, height = ceil(max(xs)), ceil(max(ys))  # No negative positions allowed, no need to subtract min(xs|ys)
        self.l = max((width, height))
        # TODO support rectangular boards
        self.cells_per_row = int(ceil(self.l / (interaction_radius + 2 * max_radius)))

        # Create board and put particles in it
        board = self.create_board(self.cells_per_row, self.cells_per_row)

        for particle in particles:
            row, col = self.get_cell(particle, board, self.l)
            # TODO: If a particle has EXACTLY the same x or y as the side length, we get out of bounds
            board[row][col].particles.append(particle)

        return board

    def get_cell(self, particle, board, side_length):
        """Gets the cell to which a given particle belongs in a given board"""

        row, col = int(particle.y / side_length * self.cells_per_row), int(particle.x / side_length * self.cells_per_row)
        return row, col  # Return array indices rather than raw (x,y)

    def create_board(self, width, height):
        board = []
        for y in range(height):  # TODO: Support rectangular boards?
            board.append([])
            for x in range(width):
                board[y].append(CellIndexMethod.Cell(y, x))

        return board

    class Cell:

        def __init__(self, row, col, particles=None, is_fake= False):
            if particles is None:
                particles = []
            self.row = row
            self.col = col
            self.particles = particles
            self.is_fake = is_fake

        # def getNeighborCells(self, board: CellIndexMethod):
        def getNeighborCells(self, board):
            """Gets neighboring cells above and to the right of the cell that are within the board. Ver teórica 1
            filmina 24. """

            result = []
            for delta_row in [1, 0, -1]:
                for delta_col in [0, 1]:
                    # Skip self and neighbor directly below
                    if delta_row == delta_col == 0 or (delta_row == -1 and delta_col == 0):
                        continue

                    col, row, = self.col + delta_col, self.row + delta_row
                    cells_per_row = board.cells_per_row
                    # Only add cells within the board
                    if 0 <= col < cells_per_row and 0 <= row < cells_per_row:
                        result.append(board.board[row][col])
                    elif board.is_periodic:
                        particles = []
                        # Create fake cells with fake coordinates for infinite boards
                        delta_x = delta_y = 0
                        if col < 0:
                            delta_x = -board.l
                        elif col >= board.cells_per_row:
                            delta_x = board.l
                        if row < 0:
                            delta_y = -board.l
                        elif row >= board.cells_per_row:
                            delta_y = board.l

                        for original_particle in board.board[row % board.cells_per_row][col % board.cells_per_row].particles:
                            particles.append(Particle(original_particle.x + delta_x, original_particle.y + delta_y, original_particle.radius, True, original_particle))

                        result.append(CellIndexMethod.Cell(row, col, particles, True))

            return result

        def getNeighborParticles(self, board):

            result = []
            for cell in self.getNeighborCells(board) + [self]:
                result += cell.particles

            return result

        def __str__(self):
            return "%sCell @ (%i, %i) with %i particles" % ("Fake " if self.is_fake else "", self.col, self.row, len(self.particles))