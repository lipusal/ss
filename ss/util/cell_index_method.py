from collections import defaultdict
from math import ceil

class CellIndexMethod:
    def __init__(self, *particles, interaction_radius):
        self.particles = particles
        self.interactionRadius = interaction_radius
        self.cells = self.particlesInCells(particles, interaction_radius)

        self.distances = self.calculateDistances(interaction_radius)

    # TODO: Ver si queda interactionRadius o no
    def calculateDistances(self, interactionRadius=-1):
        result = defaultdict(defaultdict)  # Dictionary that returns a new dictionary when accessing a nonexistent key
        if (interactionRadius == -1):
            interactionRadius = self.interactionRadius
        for cell in self.cells:
            for ownParticle in cell.particles:
                for neighbor in cell.getNeighborParticles(self):
                    result[TODO cell ID][TODO other cell ID] = result[TODO other cell ID][TODO cell ID] = ownParticle.distanceTo(neighbor)
        return result

        # TODO: When returning, remove default dict behavior
        # TODO NOW

    def getCell(self, particle):
        row, col = int(particle.y / self.sideLength * self.cellsPerRow), int(
            particle.x / self.sideLength * self.cellsPerRow)
        return (row, col)

    def particlesInCells(self, particles, interaction_radius):
        # Calculate minimum bounding rectangle for particles
        xs = ys = []
        max_radius = 0
        for particle in particles:
            xs.append(particle.x)
            ys.append(particle.y)
            max_radius = max((max_radius, particle.radius))

        width, height = max(xs) - min(xs), max(ys) - min(ys)
        l = max((width, height))
        cells_per_row = ceil(l / (interaction_radius + 2*max_radius))
        result =[CellIndexMethod.Cell(i, j)] for i in range(self.cellsPerRow)



        # List (rows) of lists (columns) of lists (particles)
        result = [[CellIndexMethod.Cell(i, j) for j in range(self.cellsPerRow)] for i in range(self.cellsPerRow)]
        for particle in self.particles:
            row, col = self.getCell(particle)
            result[row][col].particles.append(particle)

        return result

    class Cell:

        def __init__(self, row, col, particles=[]):
            self.row = row
            self.col = col
            self.particles = particles

        # def getNeighborCells(self, board: CellIndexMethod):
        def getNeighborCells(self, board):
            """Gets neighboring cells above and to the right of the cell that are within the board. Ver teórica 1
            filmina 24. """
            cells = board.cells
            result = []
            for deltaY in [1, 0, -1]:
                for deltaX in [0, 1]:
                    # Skip self and neighbor directly below
                    if deltaY == deltaX == 0 or (deltaY == -1 and deltaX == 0):
                        continue

                    x, y, = self.col + deltaX, self.row + deltaY
                    # Only add cells within the board
                    if 0 <= x < board.cellsPerRow and 0 <= y < board.cellsPerRow:
                        result.append(cells[y][x])

            return result

        # def getNeighborParticles(self, board: CellIndexMethod):
        def getNeighborParticles(self, board):

            result = []
            for cell in self.getNeighborCells(board):
                result += cell.particles

            return result
