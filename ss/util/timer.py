# Adapted from https://stackoverflow.com/a/12344609/2333689
# Made for Python 3

import atexit
from time import time
from datetime import timedelta

separator = "=" * 40


def seconds_to_str(t):
    return str(timedelta(seconds=t))


def log(s, elapsed=None):
    print(separator)
    print(s)
    if elapsed:
        print("Elapsed time:", elapsed)
    print(separator)
    print()


def endlog():
    end = time()
    elapsed = end - start
    log("Timer End", seconds_to_str(elapsed))


def now():
    return seconds_to_str(time())


start = time()
atexit.register(endlog)
log("Timer Start")
