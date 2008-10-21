from __future__ import with_statement

from pycucumber import Given, When, Then, Test
import sys


if __name__ == "__main__":
    with open(sys.argv[1]) as file:
        Test("".join(file.readlines()))
