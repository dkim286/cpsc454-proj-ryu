#!/usr/bin/env python3
import time
import sys

class ICMP_Detector:
    '''
    Keeps track of the number of ICMP packets sent by each host. Tolerates only
    up to 100 pings/sec.
    Maintains a dict() of {IP: [count,timestamp]} mapping that keeps track of
    how many pings are sent by each address.
    Any data older than 1 sec are thrown out.
    '''
    def __init__(self):
        self._icmp_count = dict()


    def icmp_sent(self, src):
        '''
        Call this function only when `src` sends an ICMP packet.
        This function DOES NOT perform ICMP detection on its own.

        Params:
            src (str): MAC address of the source of ICMP package (ping).

        Returns:
            (bool): True if there's a potential flooding attack. False otherwise.
        '''
        # new ping source detected
        if src not in self._icmp_count.keys():
            print('new ping source: ', src)
            self._icmp_count[src] = [1, time.time()]
        # IP is already in the entry
        else:
            now = time.time()
            elapsed_time = now - self._icmp_count[src][1]
            # don't let the tally overflow into something nonsensical
            if self._icmp_count[src][0] == sys.maxsize:
                self._icmp_count[src] = [1, now]
            # don't care about data older than 1 second. discard it.
            elif elapsed_time > 1:
                self._icmp_count[src] = [1, now]
            else:
                self._icmp_count[src][0] += 1
            #print('ping count from ', src, ': ', self._icmp_count[src][0])

        return self._check_flooding()


    def _check_flooding(self, tolerance=100):
        '''
        WARNING: this function is meant to be called by icmp_sent(). Calling this
        function anywhere else will yield unexpected results.
        Check if there's an ICMP flooding going on by analyzing the internal
        IP-to-count mapping.

        Params:
            tolerance (int): Optional. Tolerate up to this many pings/sec.

        Returns:
            (bool): True if any hosts are sending pings/sec rate that exceeds the
                    tolerance value. False otherwise.
        '''
        # Tolerate only up to 100 pings/sec from one source.
        for key in self._icmp_count:
            elapsed_time = time.time() - self._icmp_count[key][1]
            rate = self._icmp_count[key][0] / elapsed_time
            # Give it a quarter-second leeway to prevent false positives on
            # single-ping traffic.
            if rate >= tolerance and elapsed_time > 0.25:
                return True
        return False
