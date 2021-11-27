#!/usr/bin/env python3
import time
from abc import ABC, abstractclassmethod

MAX_ATTACKS = 500       # only tolerate 500 hits/sec
TIMEOUT = 1             # 1 second

class Trigger(ABC):
    @abstractclassmethod
    def detect(self, switch, message, context):
        pass


class Trigger_UDP(Trigger):
    def __init__(self):
        self._monitoring = False
        self._count = 0
        self._time_start = 0
        self._mac = { 'prev': '',  }
        # TODO: this is a stupid idea. i need to implement the fucking firewall in openflow and ryu first.

    def detect(self, switch, message, context):
        if not self._monitoring:
            self._monitoring = True
            self._time_start = time.time()

        if time.time() - self._time_start > TIMEOUT:
            # packet arrived past the 1sec time window, so ignore it
            self._count = 0
