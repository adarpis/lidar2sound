#!/usr/bin/env python3
"""Sweep scanner emulator
"""
#__all__ = ['help']
__author__ = "Adrian Arpi <aarpi@imaytec.com>"
__date__ = "20 February 2019"

__credits__ = """Guido van Rossum, for an excellent programming language.
Edy Ayala and Universidad Politecnica Salesiana, for all theirs support on this.
"""

# Known bugs that can't be fixed here:
#   - 

import collections
from time import sleep

class Scan(collections.namedtuple('Scan', 'samples')):
    pass


class Sample(collections.namedtuple('Sample', 'angle distance signal_strength')):
    pass


class Sweep:
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def get_scans(self):
        num_samples = 100
        angles = [angle for angle in range(0,360000, int(360000/num_samples))]
        distances = [distance for distance in range(4000,0, int(-4000/num_samples))]
        signal_strengths = [200] * num_samples

        while True:
            samples = [Sample(angle=angles[n],
                            distance=distances[n],
                            signal_strength=signal_strengths[n]) 
                            for n in range(num_samples)]

            sleep(0.5)

            yield Scan(samples=samples)

    def __exit__(self, *args):
        pass
