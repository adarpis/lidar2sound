#!/usr/bin/env python3
"""Translate data from LIDAR Scanse to OSC format. This is used to command
Sonic Pi script attached as part of this project
"""
#__all__ = ['help']
__author__ = "Adrian Arpi <aarpi@imaytec.com>"
__date__ = "20 February 2019"

__credits__ = """Guido van Rossum, for an excellent programming language.
Edy Ayala and Universidad Politecnica Salesiana, for all theirs support on this.
"""

# Known bugs that can't be fixed here:
#   - 

import sys
import queue
import threading

__if_sweeppy__ = True
try:
    from sweeppy import Sweep
except ImportError:
    __if_sweeppy__ = False

from pythonosc import osc_message_builder
from pythonosc import udp_client



# Below we create three worker threads:
#  - The producer thread continuously putting scans into an unbounded queue
#  - The consumer thread continuously pulling scans out of an unbounded queue
#  - The timer thread setting a stop event after a few seconds
#
# A few things you probably want to look out for:
#  - Make the queue bounded or make sure you can consume faster than you can
#    produce otherwise memory usage will grow over time.
#  - If you make the queue bounded look into queue `put` and `get` functions
#    and their blocking behavior. You probably want a ringbuffer semantic.



class Scanner(threading.Thread):
    def __init__(self, dev, queue, done):
        super().__init__()
        self.dev = dev
        self.queue = queue
        self.done = done

    # Iterate over an infinite scan generator and only stop
    # if we got asked to do so. In that case put a sentinel
    # value into the queue signaling the consumer to stop.
    def run(self):
        if __if_sweeppy__:
            with Sweep(self.dev) as sweep:
                sweep.start_scanning()

                for scan in sweep.get_scans():
                    if self.done.is_set():
                        self.queue.put_nowait(None)
                        break
                    else:
                        self.queue.put_nowait(scan)

                sweep.stop_scanning()
        else:
            if self.done.is_set():
                self.queue.put_nowait(None)

class SampleCounter(threading.Thread):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    # Iterate over the queue's scans blocking if the queue is
    # empty. If we see the producer's sentinel value we exit.
    #
    # We can not use the same stop event for both producer and
    # consumer because of the following potential scenario:
    #   - the queue is empty (we block in `get`)
    #   - the producer sees the event and stops
    #   - the consumer waits forever
    def run(self):
        while True:
            scan = self.queue.get()

            if not scan:
                break

            print(len(scan.samples))
            self.queue.task_done()


def main():
    if len(sys.argv) < 2:
        sys.exit('python lidar2osc.py /dev/ttyUSB0')

    dev = sys.argv[1]

    done = threading.Event()
    timer = threading.Timer(3, lambda: done.set())

    fifo = queue.Queue()

    scanner = Scanner(dev, fifo, done)
    counter = SampleCounter(fifo)

    scanner.start()
    counter.start()
    timer.start()

# def main():

#     if len(sys.argv) < 2:
#         sys.exit('python lidar2osc.py /dev/ttyUSB0')

#     sender = udp_client.SimpleUDPClient('127.0.0.1', 4559)
#     while True:
#         try:
#             for note in range(40, 120, 10):
#                 sender.send_message('/trigger/prophet', [note, 100, 0.5])    
#             for note in range(120, 40, -10):
#                 sender.send_message('/trigger/prophet', [note, 100, 0.5])
#         except KeyboardInterrupt:
#             sys.exit(0)

if __name__ == '__main__': 
    main()
