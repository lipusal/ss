from ss.util.file_reader import FileReader
from ss.cim.particle import Particle


def np(input, num_particles):
    """Read the last frame of the specified input file (NOTE: particles should be compacted in this frame, ie. all
    accumulated on the bottom of the silo and not moving), and calculate Np by dividing number of particles by occupied
    area.

    :return Np"""

    # Read last frame
    data, _ = FileReader.import_positions_ovito(input, -1)
    particles = []
    for i in range(num_particles):
        id, x, y = data[i]
        particles.append(Particle(x, y, id=id))

    xs, ys = [p.x for p in particles], [p.y for p in particles]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)

    return len(particles) / (width*height)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input file", type=str)
    parser.add_argument("num_particles", help="Number of particles to read from input file.", type=int)
    args = parser.parse_args()

    print("Np for %s = %g" % (args.input, np(args.input, args.num_particles)))
