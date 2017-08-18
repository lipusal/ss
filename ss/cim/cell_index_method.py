from math import ceil
from ss.util.ddict import Ddict
from collections import defaultdict


class CellIndexMethod:
    def __init__(self, *particles, interaction_radius):
        self.particles = particles
        self.interaction_radius = interaction_radius
        self.l = -1
        self.cells_per_row = -1
        self.board = self.particles_in_cells(particles, interaction_radius)
        self.distances = self.calculate_distances() # TODO stop using this, it's only used for debugging
        self.neighbors = self.calculate_neighbors()

    def calculate_distances(self):
        result = Ddict.ddict()  # Dictionary that returns a new dictionary when accessing a nonexistent key
        for row in self.board:
            for cell in row:
                for ownParticle in cell.particles:
                    for neighbor in cell.getNeighborParticles(self.board):
                        distance = ownParticle.distance_to(neighbor)
                        result[ownParticle.id][neighbor.id] = result[neighbor.id][ownParticle.id] = distance

        return Ddict.to_dict(result)

    def calculate_neighbors(self):
        result = defaultdict(list)
        for row in self.board:
            for cell in row:
                for ownParticle in cell.particles:
                    for neighbor in cell.getNeighborParticles(self.board):
                        distance = ownParticle.distance_to(neighbor)
                        if distance <= self.interaction_radius:
                            if ownParticle.id not in result:
                                result[ownParticle.id] = []
                            if neighbor.id not in result:
                                result[neighbor.id] = []

                            result[ownParticle.id].append(neighbor)
                            result[neighbor.id].append(ownParticle)
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

        def __init__(self, row, col, particles=None):
            if particles is None:
                particles = []
            self.row = row
            self.col = col
            self.particles = particles

        # def getNeighborCells(self, board: CellIndexMethod):
        def getNeighborCells(self, board):
            """Gets neighboring cells above and to the right of the cell that are within the board. Ver teórica 1
            filmina 24. """

            result = []
            for deltaY in [1, 0, -1]:
                for deltaX in [0, 1]:
                    # Skip self and neighbor directly below
                    if deltaY == deltaX == 0 or (deltaY == -1 and deltaX == 0):
                        continue

                    x, y, = self.col + deltaX, self.row + deltaY
                    cells_per_row = len(board)
                    # Only add cells within the board
                    # TODO: Support infinite boards
                    if 0 <= x < cells_per_row and 0 <= y < cells_per_row:
                        result.append(board[y][x])

            return result

        def getNeighborParticles(self, board):

            result = []
            for cell in self.getNeighborCells(board) + [self]:
                result += cell.particles

            return result
