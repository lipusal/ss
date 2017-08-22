import re
from ss.cim.particle import Particle


class FileReader:
    """Utility class used for importing particle positions and radii from files"""

    @staticmethod
    def import_particles(dynamic_file_path, static_file_path='static.txt'):
        """Imports particles from a given dynamic file (mandatory) and static file (optional). Returns an object of the
        form `{t, particles, properties}`."""

        dynamic_file = open(dynamic_file_path, 'r')
        try:
            static_file = open(static_file_path, 'r')
        except FileNotFoundError:
            static_file = None
            print('Static file not found, falling back to radius = 0')

        t = int(dynamic_file.readline())        # Unused?
        positions = []
        for line in dynamic_file:
            numbers = re.split(" +", line.strip())          # Get X and Y
            positions.append(list(map(float, numbers)))     # Convert each string to number

        num_particles = len(positions)
        radii = []
        properties = []
        if not static_file is None:
            static_particles = int(static_file.readline())
            if static_particles != num_particles:
                raise Exception("Static file has %i particles while dynamic file has %i, aborting." % (
                static_particles, num_particles))

            board_side_length = int(static_file.readline())  # Unused
            for line in static_file:
                radius, property = re.split(" +", line.strip())
                radii.append(float(radius))
                # TODO what to do with property?

        particles = []
        for i in range(num_particles):
            particles.append(Particle(positions[i][0], positions[i][1], radii[i]))

        return {'t': t, 'particles': particles, 'properties': properties}
