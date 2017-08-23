from math import ceil
from ss.util.ddict import Ddict
from collections import defaultdict
from ss.cim.cell import Cell

class CellIndexMethod:
    def __init__(self, *particles, interaction_radius, is_periodic=False):
        self.particles = particles
        self.interaction_radius = interaction_radius
        self.is_periodic = is_periodic
        self.l = -1
        self.cells_per_row = -1
        self.board = self.particles_in_cells(particles, interaction_radius)
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
                            result[me.id].append((neighbor.original_particle if neighbor.is_fake else neighbor, distance))
                            result[neighbor.original_particle.id if neighbor.is_fake else neighbor.id].append((me, distance))
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
        epsilon = 1e-5  # Quick fix to prevent bugs when particles are at EXACTLY the board limit
        width, height = ceil(max(xs)) + epsilon, ceil(max(ys) + epsilon)  # No negative positions allowed, no need to subtract min(xs|ys)
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

    #list with distances of particle with id to its corresponding neighbors
    def get_distances(self, id):
        return [x[1] for x in self.neighbors[id]]

    def create_board(self, width, height):
        board = []
        for y in range(height):  # TODO: Support rectangular boards?
            board.append([])
            for x in range(width):
                board[y].append(Cell(y, x))

        return board
