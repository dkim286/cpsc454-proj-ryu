#!/usr/bin/env python3

import time
from ryu.lib.packet import in_proto
from abc import ABC

class _counter:
    '''
    A counter object that keeps track of source MAC, number of packets, and timestamp of first detection.
    '''
    def __init__(self, src):
        self._src = src
        self._timestamp = time.time()
        self._count = 1

    @property
    def src(self):
        '''
        Source MAC address (str)
        '''
        return self._src

    @src.setter
    def src(self, new_src):
        self._src = new_src

    @property
    def timestamp(self):
        '''
        Time of first detection (float, unix epochs).
        '''
        return self._timestamp

    def set_timestamp(self):
        '''
        Set timestamp to the current time.
        '''
        self._timestamp = time.time()

    @property
    def count(self):
        '''
        Packet count.
        '''
        return self._count

    @count.setter
    def count(self, new_count):
        self._count = new_count


class Detector:
    '''
    Base class for all detectors.
    '''
    def tally(self, src):
        # new packet source detected
        if src not in self._mapping.keys():
            self._mapping[src] = _counter(src)
        else:
            now = time.time()
            elapsed_time = now - self._mapping[src].timestamp
            # don't care about data older than 1 second. discard it.
            if elapsed_time > 1:
                self._mapping[src] = _counter(src)
            else:
                self._mapping[src].count += 1
        return self._check_flooding()

    def seen(self, src):
        '''
        Returns True if src was seen sending packets before. False otherwise.
        '''
        return src in self._mapping.keys()


    def reset(self, src):
        '''
        Reset packet count for src.
        '''
        self._mapping[src] = _counter(src)


    @property
    def tolerance(self):
        return self._tolerance

    @tolerance.setter
    def tolerance(self, new_tolerance, protocol):
        self._tolerance = new_tolerance
        self._protocol = protocol


    def __init__(self, tolerance=100):
        '''
        Construct a new detector object.

        Params:
            tolerance(int): amount of packets per second to tolerate for this detector.
        '''
        # {'mac_addr': _counter, ...}
        self._mapping = dict()
        self._tolerance = tolerance


    def __new__(cls, *args, **kwargs):
        '''
        Prevent direct instantiation of Detector.
        '''
        if cls is Detector:
            raise TypeError(f"Instantiating '{cls.__name__}' directly is not allowed. Extend it with another class.")
        return object.__new__(cls, *args, **kwargs)


    def _check_flooding(self):
        '''
        Go through each element in the mapping.

        Returns:
            (list of str): a list of MAC addresses sending more packets/sec than the tolerance amount.
        '''
        result = []
        for key in self._mapping:
            elapsed_time = time.time() - self._mapping[key].timestamp
            rate = self._mapping[key].count / elapsed_time
            if rate >= self._tolerance and elapsed_time > 0.25:
                result.append(key)
        return result
