# Print a random integer between 1 and the argument passed, inclusive.
#
# USAGE: python randint.py <upper limit>

import random
import sys

if __name__ == "__main__":
    print("%d" % random.randint(1, int(sys.argv[1])))

