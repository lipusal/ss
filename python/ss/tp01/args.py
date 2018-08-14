import argparse

parser = argparse.ArgumentParser(description="Cell Index Method program, runs method on a given set of particles")
parser.add_argument("dynamic", help="Path of dynamic file from which to read time and particle positions")
parser.add_argument("static", nargs="?",
                    help="(Optional) Path of static file from which to read particle radii and properties",
                    default=None)
parser.add_argument("radius", help="Interaction radius for all particles.", type=float)
parser.add_argument("-l", help="Board side length. Integer. If not provided, will calculate a minimum bounding box "
                               "containing all particles", type=int)
parser.add_argument("-m", help="Cells per row. Integer. If not provided, will calculate an optimal value for the "
                               "particles", type=int)
parser.add_argument("--output", "-o", help="Path of output file. Defaults to './output.txt'", default="./output.txt")
parser.add_argument("--periodic", "-p", help="Make the board periodic (particles that go \"out of board\" come in from"
                                             "the other side", action="store_true", default=False)
parser.add_argument("--verbose", "-v", help="Print verbose information while running", action="store_true",
                    default=False)
parser.add_argument("--time", "-t", help="Print elapsed program time", action="store_true", default=False)


def parse_args():
    return parser.parse_args()
