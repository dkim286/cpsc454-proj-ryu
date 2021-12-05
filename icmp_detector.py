#!/usr/bin/env python3
import time
from detector import Detector

class ICMP_Detector(Detector):
    '''
    Keeps track of the number of ICMP packets sent by each host. Tolerates only
    up to 100 pings/sec.
    Maintains a dict() of {IP: [count,timestamp]} mapping that keeps track of
    how many pings are sent by each address.
    Any data older than 1 sec are thrown out.
    '''

    def tally(self, src):
        '''
        Prints out a message if a new ping source is detected, then calls
        Detector's tally() function to count this packet.
        '''
        if not self.seen(src):
            print('new ping source detected: ', src)
        return super().tally(src)
