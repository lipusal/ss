import re
from ss.cim.particle import Particle


class FileReader:
    """Utility class used for importing results generated by FileWriter"""

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

        num_particles = int(dynamic_file.readline())    # Even if there are multiple frames, only read the first one
        t = int(dynamic_file.readline())                # Unused?
        positions = []
        for i in range(num_particles):
            numbers = re.split("[ \t]+", dynamic_file.readline().strip())   # Get X and Y
            positions.append(list(map(float, numbers)))                     # Convert each string to number

        radii = [0] * num_particles
        properties = []
        if static_file is not None:
            static_particles = int(static_file.readline())
            if static_particles != num_particles:
                raise Exception("Static file has %i particles while dynamic file has %i, aborting." % (static_particles, num_particles))

            board_side_length = int(static_file.readline())  # Unused
            i = 0
            for line in static_file:
                radius, property = re.split("[ \t]+", line.strip())
                radii[i] = float(radius)
                i += 1
                # TODO what to do with property?

        particles = []
        for i in range(num_particles):
            particles.append(Particle(positions[i][0], positions[i][1], radius=radii[i]))

        return {'t': t, 'particles': particles, 'properties': properties}

    @staticmethod
    def import_positions_ovito(input, time=None, frame=None):
        """Import particles and their properties from a given input file. File should be one generated by
        FileWriter#export_positions_ovito

        :arg time : float
                Time at which to capture particles. If None (default), will get first frame.
        :arg frame : int
                Frame number to capture. Defaults to 1.
        :return Array of (id, x, y) and array of matching properties, as an N-tuple of floats"""

        seek_to_last = False
        if time == -1:
            if frame is not None and frame != -1:
                raise Exception("Specified frame but time is -1 (last). Either don't specify frame or specify frame == -1")
            else:
                frame = -1
                seek_to_last = True
        if frame == -1:
            if time is not None and time != -1:
                raise Exception("Specified time but frame is -1 (last). Either don't specify time or specify time == -1")
            else:
                time = -1
                seek_to_last = True

        file = open(input, 'r')
        base_data, properties = [], []

        matched = False
        seek_frame = 1
        while not matched:
            test = file.readline()
            if test == "":
                # Reached EOF
                if seek_to_last:
                    break
                else:
                    raise Exception("Could not find specified time and/or frame in file")

            num_particles = int(test)
            seek_time = float(file.readline())

            if frame is None and time is None:
                # Match first frame
                matched = True
            elif seek_time == time:
                if frame is not None and seek_time != frame:
                    raise Exception("Frame #%i matches time %g, not the specified time %g. Aborting" % (seek_frame, seek_time, time))
                else:
                    matched = True
            elif seek_frame == frame:
                if time is not None and seek_time != time:
                    raise Exception("Frame #%i matches time %g, not the specified time %g. Aborting" % (seek_frame, seek_time, time))
                else:
                    matched = True
            elif seek_to_last:
                # Match every frame, we will return the last one we captured
                matched = True
                # Reset data so we don't return the whole file
                base_data, properties = [], []

            for i in range(num_particles):
                line = file.readline().strip()
                if matched:
                    # 1st value is ID, 2nd is X, 3rd is Y, all the remaining ones are properties; convert all to floats
                    id, x, y, *remainder = map(float, re.split("[ \t]+", line))
                    base_data.append((int(id), x, y))
                    properties.append(tuple(remainder))

            if seek_to_last:
                # Keep seeking more frames, finish on EOF
                matched = False

            seek_frame += 1

        file.close()
        return base_data, properties
