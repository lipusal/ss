# Add project to python path so this can be run from the command line, https://stackoverflow.com/a/23891673/2333689
import sys
import os

# NOTE: Adjust the number of ".." to get to the project's root directory (i.e. where doc, ex, and ss are, NOT inside ss
# where cim, util, etc. are)
sys.path.append(os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..")))