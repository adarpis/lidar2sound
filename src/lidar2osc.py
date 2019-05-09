#!/usr/bin/env python3
"""Translate data from LIDAR Scanse to OSC format. This is used to command
Sonic Pi script attached as part of this project
"""
__all__ = ['help']
__author__ = "Adrian Arpi <aarpi@imaytec.com>"
__date__ = "20 February 2019"

__credits__ = """Guido van Rossum, for an excellent programming language.
Edy Ayala and Universidad Politecnica Salesiana, for all theirs support on this.
"""

# Known bugs that can't be fixed here:
#   - 

import sys

from sweeppy import Sweep

from time import sleep
from pythonosc import osc_message_builder
from pythonosc import udp_client

def main():
    sender = udp_client.SimpleUDPClient('127.0.0.1', 4559)
    while True:
        try:
            for note in range(40, 120, 10):
                sender.send_message('/trigger/prophet', [note, 100, 0.5])
                sleep(0.5)
            for note in range(120, 40, -10):
                sender.send_message('/trigger/prophet', [note, 100, 0.5])
                sleep(0.5)
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == '__main__': 
    main()
