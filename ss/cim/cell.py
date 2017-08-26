from ss.cim.particle import Particle


class Cell:
    def __init__(self, row, col, particles=None, is_fake=False):
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

                    for original_particle in board.board[row % board.cells_per_row][
                                col % board.cells_per_row].particles:
                        particles.append(Particle(original_particle.x + delta_x, original_particle.y + delta_y,
                                                  original_particle.radius, original_particle.velocity.magnitude(),
                                                  original_particle.vel_angle(), True, original_particle))

                    result.append(Cell(row, col, particles, True))

        return result

    def getNeighborParticles(self, board):

        result = []
        for cell in self.getNeighborCells(board) + [self]:
            result += cell.particles

        return result

    def __str__(self):
        return "%sCell @ (%i, %i) with %i particles" % (
            "Fake " if self.is_fake else "", self.col, self.row, len(self.particles))
