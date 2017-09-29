"""Utility script for generating a base argument parser with common arguments for all projects. When imported, other
scripts may use the parser variable to add further arguments and actually parse the arguments with their custom parser."""

import argparse

parser = argparse.ArgumentParser(description="Cell Index Method base argument parser, contains basic parameters for "
                                             "all projects. Projects should override this description to their need.")
parser.add_argument("--height", "-l", help="Board side height. Decimal. If not provided, will calculate a minimum "
                                           "height containing all particles", type=float)
parser.add_argument("--width", "-w", help="Board side width. Decimal. If not provided, will calculate a minimum width "
                                          "containing all particles", type=float)
parser.add_argument("-m", help="Cells per longest side (width or height). Integer. If not provided, will calculate an"
                               "optimal value for the particles of the simulation", type=int)
parser.add_argument("--output", "-o", help="Path of output file, if the script generates an output. Defaults to "
                                           "'./output.txt'", default="./output.txt")
parser.add_argument("--periodic", "-p", help="Make the board periodic (particles that go \"out of board\" come in from"
                                             "the other side)", action="store_true", default=False)
parser.add_argument("--verbose", "-v", help="Print verbose information while running", action="store_true",
                    default=False)
parser.add_argument("--time", "-t", help="Print elapsed program time", action="store_true", default=False)


def parse_args():
    return parser.parse_args()


def to_dict():
    """Convert parsed arguments to a dictionary"""
    return {k: v for k, v in vars(parse_args()).items()}


def to_dict_no_none():
    """Convert parsed arguments to a dictionary, discarding None-value keys"""
    return {k: v for k, v in vars(parse_args()).items() if v is not None}
