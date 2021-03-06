import math
from ss.util.ddict import Ddict
from collections import defaultdict
from ss.cim.board import Board

class CellIndexMethod:

    def check_particles_in_bounds(self, particles):
        for p in particles:
            if p.x < 0 or p.y < 0 or p.y > self.height or p.x > self.width:
                raise Exception("Particle %s is out of board bounds, board height: %d, board width: %d" %(p, self.height, self.width))

    def __init__(self, particles, **kwargs):
        self.particles = particles
        self.interaction_radius = kwargs['radius']
        self.is_periodic = kwargs.get('periodic', False)
        self.width = kwargs.get('width', -1)
        self.height = kwargs.get('height', -1)
        self.m = kwargs.get('m', -1)
        self.check_particles_in_bounds(particles)
        self.board = self.create_board()
        self.neighbors = self.calculate_neighbors()

    def calculate_distances(self):
        result = Ddict.ddict()  # Dictionary that returns a new dictionary when accessing a nonexistent key
        for row in self.board.cells:
            for cell in row:
                for me in cell.particles:
                    for neighbor in cell.getNeighborParticles(self.board):
                        if me == neighbor or neighbor in result[me.id]:
                            continue

                        distance = me.distance_to(neighbor)
                        result[me.id][neighbor.id] = result[neighbor.id][me.id] = distance

        return Ddict.to_dict(result)

    def calculate_neighbors(self):
        """Calculate neighbors of each particle optimally and return a dictionary with particle IDs as keys and neighbor
        Particle lists as values."""
        result = defaultdict(list)
        for row in self.board.cells:
            for cell in row:
                for me in cell.particles:
                    for neighbor in cell.getNeighborParticles(self.board):
                        # result[me.id] is a list of tuples, particles are in the 0 position of each tuple.
                        if me == neighbor or neighbor in [t[0] for t in result[me.id]]:
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

    def get_distances(self, id):
        """List with distances of particle with id to its corresponding neighbors"""
        return [x[1] for x in self.neighbors[id]]

    def create_board(self):
        """Creates the board to be used for this run of the Cell Index Method. Fills in missing board parameters if
        necessary:
            - Width
            - Height
            - M

        :return The created board
        """

        if self.width == -1 or self.height == -1:
            width, height = Board.calculate_mbb(self.particles)
            if self.width == -1:
                self.width = width
            if self.height == -1:
                # TODO: If height not provided, assume square board unless the particles would end up outside the board?
                # i.e:  self.height = max(self.width, height)
                self.height = height

        l = max(self.width, self.height)
        if self.m == -1:
            # Calculate max particle radius
            max_radius = max([p.radius for p in self.particles])

            # Compute optimal board parameters
            self.m = math.ceil(l / (self.interaction_radius + 2 * max_radius))
            if l / self.m <= self.interaction_radius:
                # FIXME: This shouldn't happen, revise previous formula
                # print("WARNING: The calculated M (%i) is over limit, restricting to " % self.m, end="")
                self.m = math.floor(l / self.interaction_radius) - 1
                # print(self.m)

        if l / self.m <= self.interaction_radius:
            raise Exception("L / M > Rc is not met, can't perform cell index method, aborting. (L = %g, M = %g, "
                            "Rc = %g)" % (l, self.m, self.interaction_radius))

        board = Board(self.particles, width=self.width, height=self.height, is_periodic=self.is_periodic,
                      cell_side_length=l/self.m)
        return board

    def __str__(self):
        result = ""
        for row in reversed(range(self.board.num_rows)):
            result += '|'
            for col in range(self.board.num_cols):
                result += "%i|" % len(self.board.cells[row][col].particles)
            result += "\n"
        return result
