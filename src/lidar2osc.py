#!/usr/bin/env python3
"""Translate data from LIDAR Scanse to OSC format. This is used to command
Sonic Pi script attached as part of this project
"""
#__all__ = ['help']
__author__ = "Adrian Arpi <aarpi@imaytec.com>"
__date__ = "20 February 2019"

__credits__ = """Guido van Rossum, for an excellent programming language.
Edy Ayala and Universidad Politecnica Salesiana, for all theirs support on this project.
"""

# Known bugs that can't be fixed here:
#   -

import sys
import queue
import threading
from time import sleep

__if_sweeppy__ = True
try:
    from sweeppy import Sweep
except ImportError:
    from emu_sweepy import Sweep
    __if_sweeppy__ = False

from pythonosc import osc_message_builder
from pythonosc import udp_client

from statistics import median


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
                        #sweep.set_motor_speed(0)
                        self.queue.put_nowait(None)
                        break
                    else:
                        self.queue.put_nowait(scan)

                sweep.stop_scanning()
        else:
            with Sweep() as sweep:

                for scan in sweep.get_scans():
                    if self.done.is_set():
                        self.queue.put_nowait(None)
                        break
                    else:
                        self.queue.put_nowait(scan)


class TriggerOSC(threading.Thread):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.sender = udp_client.SimpleUDPClient('127.0.0.1', 4559)
        self.decimate = 0

    def __sweep2osc(self, scan):
        num_notes = 14
        r_coverage = 30
        rnotes = [[] for i in range(num_notes)]
        for angle, distance, signal_strength in scan.samples:
            if signal_strength > 150 and angle >= 0 and angle <= 360000 and distance < r_coverage:
                rnotes[int(round(angle * ((num_notes-1)/360000)))].append(r_coverage - distance)
        for i, note in enumerate(rnotes):
            if not note:
                rnotes[i].append(0)
                
        notes = [median(note)/r_coverage for note in rnotes]
        print(notes)
        self.sender.send_message('/trigger/prophet', notes)

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
                print('Expiration time has been over. Stopping execution')
                break

            print(len(scan.samples))
            if self.decimate < 4:
                self.decimate += 1
            else:
                self.__sweep2osc(scan)
                self.decimate = 0
            self.queue.task_done()


def main():
    if len(sys.argv) < 2:
        sys.exit('python lidar2osc.py /dev/ttyUSB0')

    if not __if_sweeppy__:
        print('SweepPy module is nedded, '
              'please check https://github.com/scanse/sweep-sdk/tree/master/sweeppy '
              'Actually is running a emulator for test porpuses')

    dev = sys.argv[1]

    done = threading.Event()
    timer = threading.Timer(300, lambda: done.set())

    fifo = queue.Queue()

    scanner = Scanner(dev, fifo, done)
    counter = TriggerOSC(fifo)

    scanner.start()
    counter.start()
    timer.start()

    while True:
        try:
            sleep(1)
            if done.is_set():
                sys.exit(0)
                break
        except KeyboardInterrupt:
            done.set()
            sys.exit(0)


if __name__ == '__main__':
    main()
