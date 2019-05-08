#!/usr/bin/env python3
"""Translate data from LIDAR Scanse to OSC format. This is used to command
Sonic Pi script attached as part of this project
"""
__all__ = ['help']
__author__ = "Adrian Arpi <aarpi@imaytec.com>"
__date__ = "20 February 2019"

__credits__ = """Guido van Rossum, for an excellent programming language.
Edy Ayala and Universidad Politecnica Salesiana, for all his support on this.
"""

# Known bugs that can't be fixed here:
#   - 

from pythonosc import osc_message_builder
from pythonosc import udp_client

sender = udp_client.SimpleUDPClient('127.0.0.1', 4559)

if __name__ == '__main__': 
    sender.send_message('/trigger/prophet', [70, 100, 8])